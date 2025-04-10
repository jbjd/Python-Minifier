import ast

SLOTS_NAME: str = "__slots__"
STATIC_METHOD_NAME = "staticmethod"


def add_slots(module: ast.Module) -> ast.Module:

    for node in module.body:
        if not isinstance(node, ast.ClassDef):
            continue

        self_assigns: list[str] = _find_all_self_assigns(node)
        self_assigns.sort()
        slots_node = _make_slots_node(self_assigns)

        existing_slots_index: int = _find_index_of_existing_slots_assign(node)
        if existing_slots_index < 0:
            node.body.append(slots_node)
        else:
            node.body[existing_slots_index] = slots_node

    return module


def _find_all_self_assigns(class_node: ast.ClassDef) -> list[str]:
    """Returns list of names of vars assigned to self in a class

    If a class only assigns "self.foo = bar" then ["foo"] is returned"""

    self_assigns: list[str] = []

    for node in class_node.body:
        if (
            not isinstance(node, ast.FunctionDef)
            or len(node.args.args) == 0
            or any(
                decorator.id == STATIC_METHOD_NAME for decorator in node.decorator_list
            )
        ):
            continue

        # TODO: Handle staticmethod
        # "self" could technically be whatever the first arg is named
        name_of_self: str = node.args.args[0].arg

        for child_node in node.body:
            if not isinstance(child_node, ast.Assign) and not isinstance(
                child_node, ast.AnnAssign
            ):
                continue

            targets: list[ast.Attribute] = (
                [child_node.target]
                if isinstance(child_node, ast.AnnAssign)
                else child_node.targets
            )

            for target in targets:
                target_name: ast.Name = target.value
                if target_name.id == name_of_self:
                    self_assigns.append(target.attr)

    return self_assigns


def _make_slots_node(self_assigns: list[str]) -> ast.Assign:

    assigns_as_constant_nodes = [ast.Constant(value=assign) for assign in self_assigns]

    name = ast.Name(id=SLOTS_NAME)
    value = ast.Tuple(assigns_as_constant_nodes)

    return ast.Assign([name], value, lineno=-1, col_offset=-1)


def _find_index_of_existing_slots_assign(class_node: ast.ClassDef) -> int:

    for i, node in enumerate(class_node.body):
        if not isinstance(node, ast.Assign) and not isinstance(node, ast.AnnAssign):
            continue

        target: ast.Attribute = (
            node.target if isinstance(node, ast.AnnAssign) else node.targets[0]
        )
        if target.id == SLOTS_NAME:
            return i

    return -1
