import ast
from ast import _Unparser  # type: ignore
from typing import Literal

from personal_python_ast_optimizer.factories.node_factory import SameLineNodeFactory
from personal_python_ast_optimizer.futures import get_ignorable_futures
from personal_python_ast_optimizer.parser.utils import (
    add_pass_if_body_empty,
    ignore_base_classes,
    is_return_none,
    remove_dangling_expressions,
    remove_empty_annotations,
)
from personal_python_ast_optimizer.python_info import (
    comparison_and_conjunctions,
    operators_and_separators,
)


class MinifyUnparser(_Unparser):

    __slots__ = (
        "module_name",
        "target_python_version",
        "within_class",
        "within_function",
    )

    def __init__(
        self,
        module_name: str = "",
        target_python_version: tuple[int, int] | None = None,
    ) -> None:
        super().__init__()
        self.module_name: str = module_name
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

    def _update_text_to_write(self, text: str) -> str:
        """Give text to be written, replace some specific occurrences"""
        if text in operators_and_separators:
            return text.strip()

        if text in comparison_and_conjunctions:
            return self._needed_space_before_expr() + text[1:]

        return text

    def visit_Pass(self, node: ast.Pass | None = None) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("pass", same_line=same_line)

    def visit_Return(self, node: ast.Return) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("return", same_line=same_line)
        if node.value and not is_return_none(node):
            self.write(" ")
            self.traverse(node.value)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Skip unnecessary futures imports"""
        if node.module == "__future__" and self.target_python_version is not None:
            ignoreable_futures: list[str] = get_ignorable_futures(
                self.target_python_version
            )
            node.names = [
                alias for alias in node.names if alias.name not in ignoreable_futures
            ]

        if not node.names:
            return

        super().visit_ImportFrom(node)

    def visit_arg(self, node: ast.arg) -> None:
        self.write(node.arg)

    def visit_arguments(self, node: ast.arguments) -> None:
        if node.kwarg:
            node.kwarg.annotation = None
        if node.vararg:
            node.vararg.annotation = None

        super().visit_arguments(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.fill()
        self.traverse(node.target)
        self.write(self.binop[node.op.__class__.__name__] + "=")
        self.traverse(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
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
            self.write(":'Any'")

    @staticmethod
    def _within_class_node(function):
        def wrapper(self: "MinifyUnparser", *args, **kwargs) -> None:
            self.within_class = True
            function(self, *args, **kwargs)
            self.within_class = False

        return wrapper

    @_within_class_node
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        remove_dangling_expressions(node)

        add_pass_if_body_empty(node)
        if len(node.body) == 1:
            self._set_can_write_same_line(node.body[0])

        if self._use_version_optimization((3, 0)):
            ignore_base_classes(node, ["object"])

        self._write_decorators(node)

        self.fill("class " + node.name)

        with self.delimit_if("(", ")", condition=node.bases or node.keywords):
            self._traverse_comma_delimited_list(node.bases)
            self._traverse_comma_delimited_list(node.keywords)

        self._traverse_body(node)

    def _traverse_comma_delimited_list(self, to_traverse: list) -> None:
        for index, node in enumerate(to_traverse):
            if index > 0:
                self.write(",")
            self.traverse(node)

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

        add_pass_if_body_empty(node)
        if len(node.body) == 1:
            self._set_can_write_same_line(node.body[0])

        self._write_decorators(node)

        def_str = f"{fill_suffix} {node.name}"
        self.fill(def_str)

        with self.delimit("(", ")"):
            self.traverse(node.args)

        self._traverse_body(node)

    def _write_decorators(self, node: ast.ClassDef | ast.FunctionDef) -> None:
        for decorator in node.decorator_list:
            self.fill("@")
            self.traverse(decorator)

    def _traverse_body(self, node: ast.ClassDef | ast.FunctionDef) -> None:
        with self.block():
            self.traverse(node.body)

    def _needed_space_before_expr(self) -> str:
        if not self._source:
            return ""
        most_recent_token: str = self._source[-1]
        return "" if most_recent_token[-1:] in ("'", '"', ")", "]", "}") else " "

    def _use_version_optimization(self, python_version: tuple[int, int]) -> bool:
        if self.target_python_version is None:
            return False

        return self.target_python_version >= python_version

    @staticmethod
    def _set_can_write_same_line(node: ast.stmt) -> None:
        node.write_same_line = True  # type: ignore

    @staticmethod
    def _get_can_write_same_line(node: ast.stmt | None) -> bool:
        return getattr(node, "write_same_line", False)
