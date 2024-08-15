import ast
from ast import _Unparser  # type: ignore
from typing import Literal, override

from parser_utils import remove_function_dangling_expressions


class MinifyUnparser(_Unparser):

    @override
    def fill(self, text: str = "", same_line: bool = False) -> None:
        """Overrides super fill to use tabs over spaces"""
        if same_line:
            self.write(text)
        else:
            self.maybe_newline()
            self.write("\t" * self._indent + text)

    @override
    def visit_Pass(self, node: ast.Pass) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("pass", same_line=same_line)

    @override
    def visit_Return(self, node: ast.Return) -> None:
        same_line: bool = self._get_can_write_same_line(node)
        self.fill("return", same_line=same_line)
        if node.value:
            self.write(" ")
            self.traverse(node.value)

    @override
    def visit_arg(self, node: ast.arg) -> None:
        self.write(node.arg)

    @override
    def write(self, *text: str) -> None:
        text = tuple(map(self._update_text_to_write, text))
        self._source.extend(text)

    @staticmethod
    def _update_text_to_write(text: str) -> str:
        """Give text to be written, replace some specific occurancces"""
        match text:
            case ", ":
                return ","

            case _:
                return text

    @override
    def _function_helper(
        self, node: ast.FunctionDef, fill_suffix: Literal["def", "async def"]
    ) -> None:
        """Removes doc strings and type hints from function definitions"""
        remove_function_dangling_expressions(node)

        self.maybe_newline()
        for decorator in node.decorator_list:
            self.fill("@")
            self.traverse(decorator)

        def_str = f"{fill_suffix} {node.name}"
        self.fill(def_str)

        with self.delimit("(", ")"):
            self.traverse(node.args)

        # If a function was only dangling expressions, like a doc string
        # It needs to be filled with a pass to be valid
        if not node.body:
            node.body.append(ast.Pass())

        with self.block():
            if len(node.body) == 1:
                self._set_can_write_same_line(node.body[0])
            self.traverse(node.body)

    @staticmethod
    def _set_can_write_same_line(node: ast.stmt) -> None:
        node.write_same_line = True

    @staticmethod
    def _get_can_write_same_line(node: ast.stmt) -> bool:
        return getattr(node, "write_same_line", False)


def run_minify_parser(source: str) -> str:
    parsed_source: ast.Module = ast.parse(source)
    code_cleaner: MinifyUnparser = MinifyUnparser()
    cleaned_source: str = code_cleaner.visit(ast.NodeTransformer().visit(parsed_source))

    return cleaned_source
