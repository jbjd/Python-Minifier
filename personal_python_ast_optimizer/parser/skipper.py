import ast
import warnings
from typing import Literal

from personal_python_ast_optimizer.futures import get_ignorable_futures
from personal_python_ast_optimizer.parser.config import (
    SectionsToSkipConfig,
    SkipConfig,
    TokensToSkipConfig,
)
from personal_python_ast_optimizer.parser.utils import (
    get_node_name,
    is_name_equals_main_node,
    skip_base_classes,
    skip_decorators,
)


class AstNodeSkipper:

    __slots__ = (
        "source",
        "module_name",
        "target_python_version",
        "sections_to_skip_config",
        "tokens_to_skip_config",
    )

    def __init__(self, source: ast.Module, skip_config: SkipConfig) -> None:
        self.source: ast.Module = source
        self.module_name: str = skip_config.module_name
        self.target_python_version: tuple[int, int] | None = (
            skip_config.target_python_version
        )
        self.sections_to_skip_config: SectionsToSkipConfig = (
            skip_config.sections_to_skip_config
        )
        self.tokens_to_skip_config: TokensToSkipConfig = (
            skip_config.tokens_to_skip_config
        )

    def skip_sections_of_module(self) -> None:
        if (
            self.target_python_version is None
            and not self.tokens_to_skip_config.has_code_to_skip()
            and not self.sections_to_skip_config.has_code_to_skip()
        ):
            # No optimizations to do
            return

        depth: int = 0
        ast_stack: list[ast.AST] = [self.source]

        while ast_stack:
            current_node = ast_stack.pop()
            self._check_node_body(current_node, "body", depth, ast_stack)

            if isinstance(current_node, ast.If):
                self._check_node_body(current_node, "orelse", depth, ast_stack)

            depth += 1

        for tokens_to_skip in self.tokens_to_skip_config:
            not_found_tokens: list[str] = [
                t
                for t in tokens_to_skip.get_not_found_tokens()
                if t not in self.tokens_to_skip_config.no_warn
            ]
            if not_found_tokens:
                warnings.warn(
                    (
                        f"{self.module_name}: requested to skip "
                        f"{tokens_to_skip.token_type} {', '.join(not_found_tokens)}"
                        " but was not found"
                    )
                )

    def _check_node_body(
        self,
        node: ast.AST,
        body_attr: Literal["body", "orelse"],
        depth: int,
        ast_stack: list[ast.AST],
    ) -> None:
        new_node_body = []

        for child_node in getattr(node, body_attr):
            if not self._should_skip_node(child_node):
                if self._remove_skippable_tokens(child_node):
                    new_node_body.append(child_node)
                    if hasattr(child_node, "body"):
                        ast_stack.append(child_node)

        # TODO: Handle this in a better way
        if not new_node_body and (depth == 0 or body_attr == "orelse"):
            setattr(node, body_attr, [])
        else:
            if not new_node_body:
                new_node_body = [ast.Pass()]
            setattr(node, body_attr, new_node_body)

    def _should_skip_node(self, node: ast.AST) -> bool:
        """Returns if a node should be skipped based on configs"""
        if self.sections_to_skip_config.skip_name_equals_main and isinstance(
            node, ast.If
        ):
            return is_name_equals_main_node(node.test)

        if isinstance(node, ast.ClassDef):
            return node.name in self.tokens_to_skip_config.classes

        if isinstance(node, ast.FunctionDef):
            return node.name in self.tokens_to_skip_config.functions

        if isinstance(node, ast.Assign) or isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.value, ast.Call)
                and get_node_name(node.value.func)
                in self.tokens_to_skip_config.functions
            ):
                return True

            if isinstance(node, ast.AnnAssign):
                return (
                    get_node_name(node.target) in self.tokens_to_skip_config.variables
                )
            else:
                # TODO: Currently if a.b.c.d only "c" and "d" are checked
                var_name: str = get_node_name(node.targets[0])
                parent_var_name: str = get_node_name(
                    getattr(node.targets[0], "value", object)
                )
                return (
                    var_name in self.tokens_to_skip_config.variables
                    or parent_var_name in self.tokens_to_skip_config.variables
                )

        if isinstance(node, ast.Expr):
            return (
                isinstance(node.value, ast.Call)
                and get_node_name(node.value.func)
                in self.tokens_to_skip_config.functions
            )

        return False

    def _remove_skippable_tokens(self, node: ast.AST) -> bool:
        """Removes decorators, dict keys, and from imports.
        Returns False if node would now be empty can be entirely removed"""
        if isinstance(node, ast.ClassDef):
            if self._use_version_optimization((3, 0)):
                skip_base_classes(node, ["object"])

            skip_base_classes(node, self.tokens_to_skip_config.classes)
            skip_decorators(node, self.tokens_to_skip_config.decorators)

        elif isinstance(node, ast.FunctionDef):
            skip_decorators(node, self.tokens_to_skip_config.decorators)

        elif (
            isinstance(node, ast.Assign) or isinstance(node, ast.AnnAssign)
        ) and isinstance(node.value, ast.Dict):
            new_dict = {
                k: v
                for k, v in zip(node.value.keys, node.value.values)
                if getattr(k, "value", "") not in self.tokens_to_skip_config.dict_keys
            }
            node.value.keys = list(new_dict.keys())
            node.value.values = list(new_dict.values())

        elif isinstance(node, ast.ImportFrom):
            node.names = [
                alias
                for alias in node.names
                if alias.name not in self.tokens_to_skip_config.from_imports
            ]

            if node.module == "__future__" and self.target_python_version is not None:
                ignoreable_futures: list[str] = get_ignorable_futures(
                    self.target_python_version
                )
                node.names = [
                    alias
                    for alias in node.names
                    if alias.name not in ignoreable_futures
                ]

            if not node.names:
                return False

        return True

    def _use_version_optimization(self, min_version: tuple[int, int]) -> bool:
        if self.target_python_version is None:
            return False

        return self.target_python_version >= min_version
