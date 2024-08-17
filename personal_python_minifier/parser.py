import ast
from ast import _Unparser  # type: ignore
from typing import Iterable, Literal

from personal_python_minifier.factories.node_factory import SameLineNodeFactory
from personal_python_minifier.futures import get_ignorable_futures
from personal_python_minifier.parser_utils import (
    add_pass_if_body_empty,
    ignore_base_classes,
    remove_dangling_expressions,
    remove_empty_annotations,
)


class MinifyUnparser(_Unparser):

    def __init__(self, target_python_version: tuple[int, int] | None = None) -> None:
        super().__init__()
        self.target_python_version: tuple[int, int] | None = target_python_version

        self.within_class: bool = False
        self.within_function: bool = False

    def fill(self, text: str = "", same_line: bool = False) -> None:
        """Overrides super fill to use tabs over spaces"""
        if same_line:
            self.write(text)
        else:
            self.maybe_newline()
            self.write("\t" * self._indent + text)

    def write(self, *text: str) -> None:
        """Write text, with some mapping replacements"""
        text = tuple(map(self._update_text_to_write, text))
        self._source.extend(text)

    @staticmethod
    def _update_text_to_write(text: str) -> str:
        """Give text to be written, replace some specific occurancces"""
        match text:
            case ", ":
                return ","
            case " = ":
                return "="
            case " := ":
                return ":="

            case _:
                return text

    def visit_Pass(self, node: ast.Pass) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("pass", same_line=same_line)

    def visit_Return(self, node: ast.Return) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("return", same_line=same_line)
        if node.value:
            self.write(" ")
            self.traverse(node.value)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Skip unnecessary futures imports"""
        if node.module == "__future__" and self.target_python_version is not None:
            ignoreable_futures: list[str] = get_ignorable_futures(
                self.target_python_version
            )
            node.names = list(
                filter(lambda n: n.name not in ignoreable_futures, node.names)
            )

        if not node.names:
            return

        super().visit_ImportFrom(node)

    def visit_arg(self, node: ast.arg) -> None:
        self.write(node.arg)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.fill()
        self.traverse(node.target)
        self.write(self.binop[node.op.__class__.__name__] + "=")
        self.traverse(node.value)

    def visit_AnnAssign(self, node):
        """Only writes type annotations if necessary"""
        if not node.value and (not self.within_class or self.within_function):
            return

        self.fill()
        with self.delimit_if(
            "(", ")", not node.simple and isinstance(node.target, ast.Name)
        ):
            self.traverse(node.target)

        if node.value:
            self.write("=")
            self.traverse(node.value)
        elif self.within_class and not self.within_function:
            self.write(": 'Any'")

    @staticmethod
    def _within_class_node(function):
        def wrapper(self: "MinifyUnparser", *args, **kwargs) -> None:
            self.within_class = True
            function(self, *args, **kwargs)
            self.within_class = False

        return wrapper

    @_within_class_node
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

    def _write_docstring_and_traverse_body(self, node) -> None:
        if _ := self.get_raw_docstring(node):
            # Skip writing doc string
            if len(node.body) == 1:
                self.traverse(SameLineNodeFactory.create_pass())
            else:
                self.traverse(node.body[1:])
        else:
            self.traverse(node.body)

    @staticmethod
    def _within_function_node(function):
        def wrapper(self: "MinifyUnparser", *args, **kwargs) -> None:
            self.within_function = True
            function(self, *args, **kwargs)
            self.within_function = False

        return wrapper

    @_within_function_node
    def _function_helper(
        self, node: ast.FunctionDef, fill_suffix: Literal["def", "async def"]
    ) -> None:
        """Removes doc strings and type hints from function definitions"""
        remove_dangling_expressions(node)
        remove_empty_annotations(node)

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
