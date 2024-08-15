import ast
from ast import _Unparser  # type: ignore
from typing import Literal, override

from parser_utils import remove_function_dangling_expressions


class MinifyUnparser(_Unparser):

    @override
    def fill(self, text: str = ""):
        """Overrides super fill to use tabs over spaces"""
        self.maybe_newline()
        self.write("\t" * self._indent + text)

    @override
    def visit_arg(self, node: ast.arg):
        self.write(node.arg)

    @override
    def write(self, *text: str):
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
            self.write(":pass")
            return

        with self.block(extra=self.get_type_comment(node)):
            self._write_docstring_and_traverse_body(node)


def run_minify_parser(source: str) -> str:
    parsed_source: ast.Module = ast.parse(source)
    code_cleaner: MinifyUnparser = MinifyUnparser()
    cleaned_source: str = code_cleaner.visit(ast.NodeTransformer().visit(parsed_source))

    return cleaned_source
