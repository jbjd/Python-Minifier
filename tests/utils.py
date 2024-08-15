import ast
from typing import NamedTuple


class BeforeAndAfter(NamedTuple):
    """Input and what is expected after minifiying it"""

    before: str
    after: str


def is_python_code_valid(python_code: str) -> bool:
    try:
        ast.parse(python_code)
    except SyntaxError:
        return False

    return True
