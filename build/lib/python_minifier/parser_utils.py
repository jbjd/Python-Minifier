import ast


def remove_dangling_expressions(node: ast.FunctionDef | ast.ClassDef) -> None:
    """Removes constant daggling expression like doc strings"""
    node.body = [
        element
        for element in node.body
        if not (
            isinstance(element, ast.Expr) and isinstance(element.value, ast.Constant)
        )
    ]
