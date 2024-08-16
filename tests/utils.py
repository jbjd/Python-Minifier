import ast
from typing import NamedTuple

from personal_python_minifier.parser import run_minify_parser


class BeforeAndAfter(NamedTuple):
    """Input and what is expected after minifiying it"""

    before: str
    after: str


def run_minifiyer_and_assert_correctness(source: BeforeAndAfter):
    minified_function: str = run_minify_parser(source.before)
    assert source.after == minified_function
    assert is_python_code_valid(minified_function)


def is_python_code_valid(python_code: str) -> bool:
    try:
        ast.parse(python_code)
    except SyntaxError:
        return False

    return True
