import ast

from personal_python_ast_optimizer.parser.config import SkipConfig
from personal_python_ast_optimizer.parser.minifier import MinifyUnparser
from personal_python_ast_optimizer.parser.skipper import AstNodeSkipper


def parse_source_to_module_node(source: str) -> ast.Module:
    parsed_source: ast.Module = ast.parse(source)
    return parsed_source


def run_minify_parser(
    parser: MinifyUnparser, source: str, skip_config: SkipConfig | None = None
) -> str:
    module: ast.Module = parse_source_to_module_node(source)

    if skip_config is not None:
        skipper = AstNodeSkipper(module, skip_config)
        skipper.skip_sections_of_module()

    return parser.visit(module)
