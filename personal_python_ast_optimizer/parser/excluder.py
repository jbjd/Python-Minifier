import ast
from personal_python_ast_optimizer.parser.config import (
    SectionsToSkipConfig,
    TokensToSkipConfig,
)
from personal_python_ast_optimizer.parser.utils import (
    get_node_name,
    skip_base_classes,
    is_name_equals_main_node,
    skip_decorators,
)


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
                if _remove_skippable_tokens(child_node, tokens_to_skip_config):
                    new_node_body.append(child_node)
                    if hasattr(child_node, "body"):
                        ast_stack.append(child_node)

        # TODO: Handle this in a better way
        if not new_node_body and current_ast_node is source:
            current_ast_node.body = []
        else:
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
            return get_node_name(node.value.func) in tokens_to_skip_config.functions
        elif isinstance(node, ast.AnnAssign):
            return get_node_name(node.target) in tokens_to_skip_config.variables
        else:
            # TODO: Currently if a.b.c.d only "c" and "d" are checked
            var_name: str = get_node_name(node.targets[0])
            parent_var_name: str = get_node_name(
                getattr(node.targets[0], "value", object)
            )
            return (
                var_name in tokens_to_skip_config.variables
                or parent_var_name in tokens_to_skip_config.variables
            )

    if isinstance(node, ast.Expr):
        return (
            isinstance(node.value, ast.Call)
            and get_node_name(node.value.func) in tokens_to_skip_config.functions
        )

    return False


def _remove_skippable_tokens(
    node: ast.AST,
    tokens_to_skip_config: TokensToSkipConfig,
) -> bool:
    """Removes decorators, dict keys, and from imports.
    Returns False if node would now be empty can be entirely removed"""
    if isinstance(node, ast.ClassDef):
        skip_base_classes(node, tokens_to_skip_config.classes)
        skip_decorators(node, tokens_to_skip_config.decorators)

    elif isinstance(node, ast.FunctionType):
        skip_decorators(node, tokens_to_skip_config.decorators)

    elif isinstance(node, ast.Dict):
        new_dict = {
            k: v
            for k, v in zip(node.keys, node.values)
            if getattr(k, "value", "") not in tokens_to_skip_config.dict_keys
        }
        node.keys = list(new_dict.keys())
        node.values = list(new_dict.values())

    elif isinstance(node, ast.ImportFrom):
        node.names = [
            alias
            for alias in node.names
            if alias.name not in tokens_to_skip_config.from_imports
        ]

        if not node.names:
            return False

    return True
