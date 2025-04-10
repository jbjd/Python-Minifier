from personal_python_syntax_optimizer.parser import parse_source_to_module_node
from personal_python_syntax_optimizer.parser.slots_adder import add_slots


def test_slots_adder():
    """Should fix __slots__ with all self assigns"""
    bad_slots = """
class A:

    __slots__ = ("asdf",)

    def __init__(test) -> None:
        test.a = 123

    def asdf(self) -> None:
        self.b: int = 456

    @staticmethod
    def fasfasdf(c):
        c.b = 1
"""

    node_with_slots = add_slots(parse_source_to_module_node(bad_slots))

    assert node_with_slots.body[0].body[0].value.dims[0].value == "a"
    assert node_with_slots.body[0].body[0].value.dims[1].value == "b"
    assert len(node_with_slots.body[0].body[0].value.dims) == 2
