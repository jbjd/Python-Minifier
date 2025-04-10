import ast

import pytest
from personal_python_syntax_optimizer.parser import parse_source_to_module_node
from personal_python_syntax_optimizer.slots.adder import add_slots


def test_slots_adder():
    """Should fix __slots__ with all self assigns"""
    bad_slots = """
class A:

    __slots__ = ("asdf",)

    def __init__(test) -> None:
        foo = "bar"
        a = test.c = 456
        test.a = 123
        test.a.b.c = 789

    def asdf(self) -> None:
        self.b: int = 456

    @staticmethod
    def fasfasdf(c):
        c.b = 1
"""

    node_with_slots = add_slots(parse_source_to_module_node(bad_slots))

    assert len(node_with_slots.body[0].body[0].value.dims) == 3
    assert node_with_slots.body[0].body[0].value.dims[0].value == "a"
    assert node_with_slots.body[0].body[0].value.dims[1].value == "b"
    assert node_with_slots.body[0].body[0].value.dims[2].value == "c"


@pytest.mark.parametrize(
    "bad_slots",
    [
        (
            """
from typing import NamedTuple

class A(NamedTuple):
    foo: int
    bar: str
"""
        ),
        (
            """
from collections import namedtuple

class A(namedtuple('A',['foo','bar'])):
    foo: int
    bar: str
"""
        ),
    ],
)
def test_slots_adder_namedtuple(bad_slots: str):
    """Should not add slots to NamedTuple"""
    node_without_slots = add_slots(parse_source_to_module_node(bad_slots))

    assert all(
        isinstance(node, ast.AnnAssign) for node in node_without_slots.body[1].body
    )
