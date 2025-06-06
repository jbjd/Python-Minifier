import ast
from personal_python_ast_optimizer.parser.config import (
    SectionsToSkipConfig,
    TokensToSkipConfig,
)
from personal_python_ast_optimizer.parser.utils import is_name_equals_main_node


def skip_sections_of_module(
    source: ast.Module,
    sections_to_skip_config: SectionsToSkipConfig = SectionsToSkipConfig(),
    tokens_to_skip_config: TokensToSkipConfig = TokensToSkipConfig(),
) -> None:
    if (
        not tokens_to_skip_config.has_code_to_skip()
        and not sections_to_skip_config.has_code_to_skip()
    ):
        return

    ast_stack: list[ast.AST] = [source]

    while ast_stack:
        current_ast_node = ast_stack.pop()
        new_node_body = []

        for child_node in current_ast_node.body:
            if not _should_skip_node(
                child_node, sections_to_skip_config, tokens_to_skip_config
            ):
                new_node_body.append(child_node)
                if hasattr(child_node, "body"):
                    ast_stack.append(child_node)

        # TODO: Handle this in a better way
        current_ast_node.body = new_node_body if new_node_body else [ast.Pass()]


def _should_skip_node(
    node: ast.AST,
    sections_to_skip_config: SectionsToSkipConfig,
    tokens_to_skip_config: TokensToSkipConfig,
) -> bool:
    """Returns if a node should be skipped based on configs"""
    if sections_to_skip_config.skip_name_equals_main and isinstance(node, ast.If):
        return is_name_equals_main_node(node.test)

    if isinstance(node, ast.ClassDef):
        return node.name in tokens_to_skip_config.classes

    if isinstance(node, ast.FunctionDef):
        return node.name in tokens_to_skip_config.functions

    if isinstance(node, ast.Assign) or isinstance(node, ast.AnnAssign):
        if isinstance(node.value, ast.Call):
            return node.name in tokens_to_skip_config.functions
        else:
            # TODO
            return False

    if isinstance(node, ast.Expr):
        return (
            isinstance(node.value, ast.Call)
            and node.name in tokens_to_skip_config.functions
        )

    return False
