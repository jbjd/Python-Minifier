import ast

SLOTS_NAME: str = "__slots__"
STATIC_METHOD_NAME: str = "staticmethod"
TYPING_NAMEDTUPLE_NAME: str = "NamedTuple"
COLLECTIONS_NAMEDTUPLE_NAME: str = "namedtuple"


def add_slots(module: ast.Module) -> ast.Module:

    for node in module.body:
        if not isinstance(node, ast.ClassDef) or _is_named_tuple(node):
            continue

        self_assigns: list[str] = sorted(_find_all_self_assigns(node))

        slots_node = _make_slots_node(self_assigns)

        existing_slots_index: int = _find_index_of_existing_slots_assign(node)
        if existing_slots_index < 0:
            node.body.append(slots_node)
        else:
            node.body[existing_slots_index] = slots_node

    return module


def _is_named_tuple(class_node: ast.ClassDef) -> bool:
    """Returns bool of if class_node inherits from a named tuple varient"""
    return any(
        getattr(node, "id", "") == TYPING_NAMEDTUPLE_NAME
        or (isinstance(node, ast.Call) and node.func.id == COLLECTIONS_NAMEDTUPLE_NAME)
        for node in class_node.bases
    )


def _find_all_self_assigns(class_node: ast.ClassDef) -> set[str]:
    """Returns list of names of vars assigned to self in a class

    If a class only assigns "self.foo = bar" then ["foo"] is returned"""

    self_assigns: set[str] = set()

    for node in class_node.body:
        if (
            not isinstance(node, ast.FunctionDef)
            or len(node.args.args) == 0
            or any(
                decorator.id == STATIC_METHOD_NAME for decorator in node.decorator_list
            )
            or node.name == "__new__"
        ):
            continue

        name_of_self: str = node.args.args[0].arg

        for child_node in node.body:
            if not isinstance(child_node, ast.Assign) and not isinstance(
                child_node, ast.AnnAssign
            ):
                continue

            targets: list[ast.Attribute | ast.Name | ast.Tuple] = (
                [child_node.target]
                if isinstance(child_node, ast.AnnAssign)
                else child_node.targets
            )

            possible_self_assigns: list[ast.Attribute] = []
            for target in targets:
                if isinstance(target, ast.Attribute):
                    possible_self_assigns.append(target)
                elif isinstance(target, ast.Tuple):
                    for unpacked_target in target.dims:
                        if isinstance(unpacked_target, ast.Attribute):
                            possible_self_assigns.append(unpacked_target)

            for target in possible_self_assigns:
                while isinstance(target.value, ast.Attribute):
                    target = target.value

                target_name: ast.Name = target.value
                if target_name.id == name_of_self:
                    self_assigns.add(target.attr)

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
