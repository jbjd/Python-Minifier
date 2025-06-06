import ast

from personal_python_ast_optimizer.parser.config import (
    SectionsToSkipConfig,
    TokensToSkipConfig,
)
from personal_python_ast_optimizer.parser.excluder import skip_sections_of_module
from personal_python_ast_optimizer.parser.minifier import MinifyUnparser


def parse_source_to_module_node(source: str) -> ast.Module:
    parsed_source: ast.Module = ast.parse(source)
    return ast.NodeTransformer().visit(parsed_source)


def run_minify_parser(
    parser: MinifyUnparser,
    source: str,
    sections_to_skip_config: SectionsToSkipConfig = SectionsToSkipConfig(),
    tokens_to_skip_config: TokensToSkipConfig = TokensToSkipConfig(),
) -> str:
    module: ast.Module = parse_source_to_module_node(source)

    skip_sections_of_module(module, sections_to_skip_config, tokens_to_skip_config)

    return parser.visit(module)
