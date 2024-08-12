import ast
from ast import _Unparser  # type: ignore

from parser_utils import (
    remove_function_args_type_hints,
    remove_function_dangling_expressions,
)


class MinifyUnparser(_Unparser):
    """"""

    def fill(self, text=""):
        """Overrides super fill to use tabs over spaces"""
        self.maybe_newline()
        self.write("\t" * self._indent + text)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Removes doc strings and type hints from function definitions"""
        remove_function_dangling_expressions(node)

        # If a function was only dangling expressions, like a doc string
        # It needs to be filled with a pass to be valid
        if not node.body:
            super().visit_Pass(node)
            return

        remove_function_args_type_hints(node)

        super().visit_FunctionDef(node)


def run_minify_parser(source: str) -> str:
    parsed_source: ast.Module = ast.parse(source)
    code_cleaner: MinifyUnparser = MinifyUnparser()
    cleaned_source: str = code_cleaner.visit(ast.NodeTransformer().visit(parsed_source))

    return cleaned_source
