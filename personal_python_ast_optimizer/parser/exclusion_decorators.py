import ast
import warnings
from typing import Callable, Literal

from personal_python_ast_optimizer.parser.config import TokensToSkipConfig
from personal_python_ast_optimizer.parser.minifier import MinifyUnparser, SkipReason
from personal_python_ast_optimizer.parser.utils import (
    TokensToSkip,
    get_node_name,
    ignore_base_classes,
    is_name_equals_main_node,
)


def visit_decorator(visit, tokens_to_skip_config: TokensToSkipConfig):
    def wrapper(self: MinifyUnparser, node) -> str:
        result: str = visit(node)
        no_warn_tokens: set[str] = tokens_to_skip_config.no_warn

        for tokens_to_skip in tokens_to_skip_config:
            not_found_tokens: list[str] = [
                t
                for t in tokens_to_skip.get_not_found_tokens()
                if t not in no_warn_tokens
            ]
            if not_found_tokens:
                warnings.warn(
                    (
                        f"{self.module_name}: requested to skip "
                        f"{tokens_to_skip.token_type} {', '.join(not_found_tokens)}"
                        " but was not found"
                    )
                )

        return result

    return wrapper


def skip_dict_keys(visit_Dict: Callable, dict_keys_to_skip: TokensToSkip):
    def wrapper(self: MinifyUnparser, node: ast.Dict) -> None:
        new_dict = {
            k: v
            for k, v in zip(node.keys, node.values)
            if getattr(k, "value", "") not in dict_keys_to_skip
        }
        node.keys = list(new_dict.keys())
        node.values = list(new_dict.values())

        return visit_Dict(node)

    return wrapper


def skip_if_name_main(visit_If: Callable):
    def wrapper(self: MinifyUnparser, node: ast.If) -> SkipReason | None:
        if is_name_equals_main_node(node.test):
            if node.orelse:
                self.traverse(node.orelse)
            return SkipReason.EXCLUDED

        return visit_If(node)

    return wrapper


def skip_import_from(visit_ImportFrom: Callable, from_imports_to_skip: TokensToSkip):
    def wrapper(self: MinifyUnparser, node: ast.ImportFrom) -> None:
        """Skip unnecessary futures imports"""
        node.names = [
            alias for alias in node.names if alias.name not in from_imports_to_skip
        ]

        return visit_ImportFrom(node)

    return wrapper


def skip_class(visit_ClassDef: Callable, classes_to_skip: TokensToSkip):
    def wrapper(self, node: ast.ClassDef) -> SkipReason | None:
        if node.name in classes_to_skip:
            return SkipReason.EXCLUDED

        ignore_base_classes(node, classes_to_skip)

        return visit_ClassDef(node)

    return wrapper


def skip_func_assign(visit_Assign: Callable, functions_to_skip: TokensToSkip):
    def wrapper(self, node: ast.Assign) -> SkipReason | None:
        if (
            isinstance(node.value, ast.Call)
            and get_node_name(node.value.func) in functions_to_skip
        ):
            if _body_might_be_empty_without_pass(self):
                self.visit_Pass()
            return SkipReason.EXCLUDED

        return visit_Assign(node)

    return wrapper


def skip_func_call(visit_Call: Callable, functions_to_skip: TokensToSkip):
    def wrapper(self: MinifyUnparser, node: ast.Expr) -> SkipReason | None:
        if (
            isinstance(node.value, ast.Call)
            and get_node_name(node.value.func) in functions_to_skip
        ):
            if _body_might_be_empty_without_pass(self):
                self.visit_Pass()
            return SkipReason.EXCLUDED

        return visit_Call(node)

    return wrapper


def skip_func_def(_function_helper: Callable, functions_to_skip: TokensToSkip):
    def wrapper(
        self: MinifyUnparser,
        node: ast.FunctionDef,
        fill_suffix: Literal["def", "async def"],
    ) -> SkipReason | None:
        if node.name in functions_to_skip:
            if _body_might_be_empty_without_pass(self):
                self.visit_Pass()
            return SkipReason.EXCLUDED

        return _function_helper(node, fill_suffix)

    return wrapper


def skip_var_ann_assign(visit_AnnAssign: Callable, vars_to_skip: TokensToSkip):
    def wrapper(self: MinifyUnparser, node: ast.AnnAssign) -> SkipReason | None:
        """Only writes type annotations if necessary"""
        var_name: str = get_node_name(node.target)
        if var_name in vars_to_skip:
            if _body_might_be_empty_without_pass(self):
                self.visit_Pass()
            return SkipReason.EXCLUDED

        return visit_AnnAssign(node)

    return wrapper


def skip_var_assign(visit_Assign: Callable, vars_to_skip: TokensToSkip):
    def wrapper(self: MinifyUnparser, node: ast.Assign) -> SkipReason | None:

        # TODO: Currently if a.b.c.d only "c" and "d" are checked
        var_name: str = get_node_name(node.targets[0])
        parent_var_name: str = get_node_name(getattr(node.targets[0], "value", object))
        if var_name in vars_to_skip or parent_var_name in vars_to_skip:
            if _body_might_be_empty_without_pass(self):
                self.visit_Pass()
            return SkipReason.EXCLUDED

        return visit_Assign(node)

    return wrapper


def skip_decorators(_write_decorators: Callable, decorators_to_skip: TokensToSkip):
    def wrapper(self: MinifyUnparser, node: ast.ClassDef | ast.FunctionDef) -> None:
        node.decorator_list = [
            n for n in node.decorator_list if get_node_name(n) not in decorators_to_skip
        ]

        return _write_decorators(node)

    return wrapper


def _body_might_be_empty_without_pass(parser: MinifyUnparser) -> bool:
    return parser._indent > 0 and parser.previous_node_in_body is None
