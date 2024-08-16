import ast
from ast import _Unparser  # type: ignore
from typing import Iterable, Literal

from personal_python_minifier.parser_utils import (
    add_pass_if_body_empty,
    ignore_base_classes,
    remove_dangling_expressions,
)
from personal_python_minifier.factories.node_factory import SameLineNodeFactory


class MinifyUnparser(_Unparser):

    def __init__(self, target_python_version: tuple[int, int] | None = None) -> None:
        super().__init__()
        self.target_python_version: tuple[int, int] | None = target_python_version

    def fill(self, text: str = "", same_line: bool = False) -> None:
        """Overrides super fill to use tabs over spaces"""
        if same_line:
            self.write(text)
        else:
            self.maybe_newline()
            self.write("\t" * self._indent + text)

    def write(self, *text: str) -> None:
        text = tuple(map(self._update_text_to_write, text))
        self._source.extend(text)

    def visit_Pass(self, node: ast.Pass) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("pass", same_line=same_line)

    def visit_Return(self, node: ast.Return) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("return", same_line=same_line)
        if node.value:
            self.write(" ")
            self.traverse(node.value)

    def visit_arg(self, node: ast.arg) -> None:
        self.write(node.arg)

    def visit_ClassDef(
        self, node: ast.ClassDef, base_classes_to_ignore: Iterable[str] | None = None
    ) -> None:
        remove_dangling_expressions(node)

        if base_classes_to_ignore:
            ignore_base_classes(node, base_classes_to_ignore)

        if self._use_version_optimization((3, 0)):
            ignore_base_classes(node, ["object"])

        add_pass_if_body_empty(node)

        if len(node.body) == 1:
            self._set_can_write_same_line(node.body[0])

        super().visit_ClassDef(node)

    @staticmethod
    def _update_text_to_write(text: str) -> str:
        """Give text to be written, replace some specific occurancces"""
        match text:
            case ", ":
                return ","

            case _:
                return text

    def _write_docstring_and_traverse_body(self, node) -> None:
        if _ := self.get_raw_docstring(node):
            # Skip writing doc string
            if len(node.body) == 1:
                self.traverse(SameLineNodeFactory.create_pass())
            else:
                self.traverse(node.body[1:])
        else:
            self.traverse(node.body)

    def _function_helper(
        self, node: ast.FunctionDef, fill_suffix: Literal["def", "async def"]
    ) -> None:
        """Removes doc strings and type hints from function definitions"""
        remove_dangling_expressions(node)

        self.maybe_newline()
        for decorator in node.decorator_list:
            self.fill("@")
            self.traverse(decorator)

        def_str = f"{fill_suffix} {node.name}"
        self.fill(def_str)

        with self.delimit("(", ")"):
            self.traverse(node.args)

        add_pass_if_body_empty(node)

        with self.block():
            if len(node.body) == 1:
                self._set_can_write_same_line(node.body[0])
            self.traverse(node.body)

    def _use_version_optimization(self, python_version: tuple[int, int]) -> bool:
        if self.target_python_version is None:
            return False

        return self.target_python_version >= python_version

    @staticmethod
    def _set_can_write_same_line(node: ast.stmt) -> None:
        node.write_same_line = True  # type: ignore

    @staticmethod
    def _get_can_write_same_line(node: ast.stmt) -> bool:
        return getattr(node, "write_same_line", False)


def run_minify_parser(
    source: str, target_python_version: tuple[int, int] | None = None
) -> str:
    parsed_source: ast.Module = ast.parse(source)
    code_cleaner: MinifyUnparser = MinifyUnparser(target_python_version)
    cleaned_source: str = code_cleaner.visit(ast.NodeTransformer().visit(parsed_source))

    return cleaned_source
