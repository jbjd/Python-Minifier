import ast
from typing import Iterable


class CodeToSkip:

    __slots__ = "_tokens_to_skip", "token_type"

    def __init__(self, tokens_to_skip: set[str] | None, token_type: str) -> None:
        # Count how often a token got skipped, init to 0
        self._tokens_to_skip: dict[str, int] = self._set_to_dict_of_counts(
            tokens_to_skip
        )
        self.token_type: str = token_type

    def __contains__(self, key: str) -> bool:
        """Returns if token is marked to skip and
        increments internal counter when True is returned"""
        try:
            self._tokens_to_skip[key] += 1
            return True
        except KeyError:
            return False

    def empty(self) -> bool:
        return not self._tokens_to_skip

    def get_not_found_tokens(self) -> set[str]:
        return set(
            token
            for token, found_count in self._tokens_to_skip.items()
            if found_count == 0
        )

    @staticmethod
    def _set_to_dict_of_counts(input_set: set[str] | None) -> dict[str, int]:
        if not input_set:
            return {}

        return {key: 0 for key in input_set}


def get_node_id_or_attr(node) -> str:
    """Gets id or attr which both can represent var names"""
    return getattr(node, "id", "") or getattr(node, "attr", "")


def is_name_equals_main_node(node: ast.expr) -> bool:
    if not isinstance(node, ast.Compare):
        return False

    return (
        getattr(node.left, "id", "") == "__name__"
        and isinstance(node.ops[0], ast.Eq)
        and getattr(node.comparators[0], "value", "") == "__main__"
    )


def remove_dangling_expressions(node: ast.ClassDef | ast.FunctionDef) -> None:
    """Removes constant daggling expression like doc strings"""
    node.body = [
        element
        for element in node.body
        if not (
            isinstance(element, ast.Expr) and isinstance(element.value, ast.Constant)
        )
    ]


def remove_empty_annotations(node: ast.FunctionDef) -> None:
    node.body = [
        element
        for element in node.body
        if not (isinstance(element, ast.AnnAssign) and not element.value)
    ]


def ignore_base_classes(node: ast.ClassDef, classes_to_ignore: Iterable[str]) -> None:
    node.bases = [
        base for base in node.bases if getattr(base, "id", "") not in classes_to_ignore
    ]


def add_pass_if_body_empty(node: ast.ClassDef | ast.FunctionDef) -> None:
    if not node.body:
        node.body.append(ast.Pass())
