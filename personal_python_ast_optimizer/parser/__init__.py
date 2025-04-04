import ast

from personal_python_ast_optimizer.parser.minifier import MinifyUnparser


def parse_source_to_module_node(source: str) -> ast.Module:
    parsed_source: ast.Module = ast.parse(source)
    return ast.NodeTransformer().visit(parsed_source)


def run_minify_parser(parser: MinifyUnparser, source: str) -> str:
    return parser.visit(parse_source_to_module_node(source))
