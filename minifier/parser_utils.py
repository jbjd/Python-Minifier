import ast


def remove_function_dangling_expressions(node: ast.FunctionDef) -> None:
    """Removes constant daggling expression like doc strings"""
    node.body = [
        element
        for element in node.body
        if not (
            isinstance(element, ast.Expr) and isinstance(element.value, ast.Constant)
        )
    ]


def remove_function_args_type_hints(node: ast.FunctionDef) -> None:
    node.returns = None

    argument: ast.arg
    for argument in node.args.args:
        argument.annotation = None
