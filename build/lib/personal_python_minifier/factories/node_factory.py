import ast


class SameLineNodeFactory:
    """Creates ast nodes with write_same_line set to True"""

    @staticmethod
    def create_pass() -> ast.Pass:
        node = ast.Pass()
        node.write_same_line = True  # type: ignore
        return node
