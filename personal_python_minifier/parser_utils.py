import ast
from typing import Iterable


def remove_dangling_expressions(node: ast.ClassDef | ast.FunctionDef) -> None:
    """Removes constant daggling expression like doc strings"""
    node.body = [
        element
        for element in node.body
        if not (
            isinstance(element, ast.Expr) and isinstance(element.value, ast.Constant)
        )
    ]


def ignore_base_classes(node: ast.ClassDef, classes_to_ignore: Iterable[str]) -> None:
    node.bases = [
        base for base in node.bases if getattr(base, "id", "") not in classes_to_ignore
    ]


def add_pass_if_body_empty(node: ast.ClassDef | ast.FunctionDef) -> None:
    if not node.body:
        node.body.append(ast.Pass())
