import ast
from ast import _Unparser  # type: ignore
from enum import Enum
from typing import Literal

from personal_python_ast_optimizer.parser.utils import (
    add_pass_if_body_empty,
    first_occurrence_of_type,
    is_return_none,
    remove_dangling_expressions,
    remove_empty_annotations,
)
from personal_python_ast_optimizer.python_info import (
    comparison_and_conjunctions,
    operators_and_separators,
)


class SkipReason(Enum):
    ALL_SUBNODES_REMOVED = 0
    ANNOTATION = 1
    FOLDED_CONSTANT = 2
    EXCLUDED = 3


class MinifyUnparser(_Unparser):

    __slots__ = (
        "constant_vars_to_fold",
        "is_last_node_in_body",
        "module_name",
        "previous_node_in_body",
        "target_python_version",
        "within_class",
        "within_function",
    )

    def __init__(
        self,
        module_name: str = "",
        constant_vars_to_fold: dict[str, int | str] | None = None,
    ) -> None:
        self._source: list[str]  # type: ignore
        self._indent: int  # type: ignore
        super().__init__()
        self.module_name: str = module_name
        self.constant_vars_to_fold: dict[str, int | str] = (
            constant_vars_to_fold if constant_vars_to_fold is not None else {}
        )

        self.previous_node_in_body: ast.stmt | None = None
        self.is_last_node_in_body: bool = False
        self.within_class: bool = False
        self.within_function: bool = False

    def fill(self, text: str = "", splitter: Literal["", "\n", ";"] = "\n") -> None:
        """Overrides super fill to use tabs over spaces and different line splitters"""
        match splitter:
            case "\n":
                self.maybe_newline()
                self.write("\t" * self._indent + text)
            case "":
                self.write(text)
            case _:
                self.write(f";{text}")

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

    def visit_node(
        self,
        node: ast.AST,
        is_last_node_in_body: bool = False,
        last_visited_node: ast.stmt | None = None,
    ) -> SkipReason | None:
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)

        self.is_last_node_in_body = is_last_node_in_body
        self.previous_node_in_body = last_visited_node

        return visitor(node)  # type: ignore

    def traverse(self, node: list[ast.stmt] | ast.AST) -> None:
        if isinstance(node, list):
            last_visited_node: ast.stmt | None = None
            last_index = len(node) - 1
            for index, item in enumerate(node):
                # TODO: store last visited node in context and make function for
                # can use semicolon. Use new var to check if writing pass is needed in
                # exclusion
                is_last_node_in_body: bool = index == last_index
                result: SkipReason | None = self.visit_node(
                    item, is_last_node_in_body, last_visited_node
                )
                if result is None:
                    last_visited_node = item
        else:
            self.visit_node(node)

    def visit_Break(self, _: ast.Break) -> None:
        self.fill("break", splitter=self._get_line_splitter())

    def visit_Pass(self, _: ast.Pass | None = None) -> None:
        self.fill("pass", splitter=self._get_line_splitter())

    def visit_Continue(self, _: ast.Continue) -> None:
        self.fill("continue", splitter=self._get_line_splitter())

    def visit_Return(self, node: ast.Return) -> None:
        self.fill("return", splitter=self._get_line_splitter())
        if node.value and not is_return_none(node):
            self.write(" ")
            self.traverse(node.value)

    def visit_Raise(self, node: ast.Raise) -> None:
        self.fill("raise", splitter=self._get_line_splitter())

        if not node.exc:
            if node.cause:
                raise ValueError("Node can't use cause without an exception.")
            return

        self.write(" ")
        self.traverse(node.exc)

        if node.cause:
            self.write(" from ")
            self.traverse(node.cause)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> SkipReason | None:
        if self.constant_vars_to_fold:
            node.names = [
                alias
                for alias in node.names
                if alias.name not in self.constant_vars_to_fold
            ]

        if not node.names:
            return SkipReason.ALL_SUBNODES_REMOVED

        return super().visit_ImportFrom(node)

    def visit_arg(self, node: ast.arg) -> None:
        self.write(node.arg)

    def visit_arguments(self, node: ast.arguments) -> None:
        if node.kwarg:
            node.kwarg.annotation = None
        if node.vararg:
            node.vararg.annotation = None

        super().visit_arguments(node)

    def visit_Assign(self, node: ast.Assign) -> SkipReason | None:
        new_targets: list[ast.expr] = [
            target
            for target in node.targets
            if not self._is_assign_of_folded_constant(target, node.value)
        ]
        if len(new_targets) == 0:
            return SkipReason.FOLDED_CONSTANT

        node.targets = new_targets

        if isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple):
            target_elts = node.targets[0].elts
            original_target_len = len(target_elts)

            # Weird edge case: unpack contains a starred expression like *a,b = 1,2,3
            # Need to use negative indexes if a bad index comes after one of these
            starred_expr_index: int = first_occurrence_of_type(target_elts, ast.Starred)
            bad_indexes: list[int] = [
                (
                    i
                    if starred_expr_index == -1 or i < starred_expr_index
                    else original_target_len - i - 1
                )
                for i in range(len(target_elts))
                if self._is_assign_of_folded_constant(
                    target_elts[i], node.value.elts[i]
                )
            ]

            node.targets[0].elts = [
                target for i, target in enumerate(target_elts) if i not in bad_indexes
            ]
            node.value.elts = [
                target
                for i, target in enumerate(node.value.elts)
                if i not in bad_indexes
            ]

            if len(node.targets[0].elts) == 0:
                return SkipReason.FOLDED_CONSTANT
            if len(node.targets[0].elts) == 1:
                node.targets = [node.targets[0].elts[0]]
            if len(node.value.elts) == 1:
                node.value = node.value.elts[0]

        self.fill(splitter=self._get_line_splitter())
        for target in node.targets:
            self.set_precedence(ast._Precedence.TUPLE, target)  # type: ignore
            self.traverse(target)
            self.write("=")
        self.traverse(node.value)

        return None

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.fill()
        self.traverse(node.target)
        self.write(self.binop[node.op.__class__.__name__] + "=")
        self.traverse(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> SkipReason | None:
        """Only writes type annotations if necessary"""
        if node.value is None and (not self.within_class or self.within_function):
            return SkipReason.ANNOTATION

        if self._is_assign_of_folded_constant(node.target, node.value):
            return SkipReason.FOLDED_CONSTANT

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

        return None

    def visit_Name(self, node: ast.Name) -> None:
        """Extends super's implementation by adding constant folding"""
        if node.id in self.constant_vars_to_fold:
            constant_value = self.constant_vars_to_fold[node.id]
            self._write_constant(constant_value)
        else:
            super().visit_Name(node)

    def _is_assign_of_folded_constant(
        self, target: ast.expr, value: ast.expr | None
    ) -> bool:
        """Returns if node is assignment of a value that we are folding. In this case,
        there is no need to assign the value since its use"""

        return (
            isinstance(target, ast.Name)
            and target.id in self.constant_vars_to_fold
            and isinstance(value, ast.Constant)
        )

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
                self.visit_Pass()
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

    def _get_line_splitter(self) -> Literal["", "\n", ";"]:
        """Get character that starts the next line of code with the shortest
        possible whitespace. Either a new line, semicolon, or nothing."""
        if (
            len(self._source) > 0
            and self._source[-1] == ":"
            and self.is_last_node_in_body
        ):
            return ""

        if isinstance(self.previous_node_in_body, ast.Assign):
            return ";"

        return "\n"
