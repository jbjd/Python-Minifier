import ast
from typing import NamedTuple

from personal_python_minifier.parser import run_minify_parser


class BeforeAndAfter(NamedTuple):
    """Input and what is expected after minifiying it"""

    before: str
    after: str


class BeforeAndAfterBasedOnVersion(NamedTuple):
    """Input and outputs it may have based on different python versions"""

    before: str
    after: dict[str]


def run_minifiyer_and_assert_correct_multiple_versions(
    source: BeforeAndAfterBasedOnVersion,
):
    for version, expected in source.after.items():
        if version is not None:
            version = _python_version_str_to_int_tuple(version)
        minified_function: str = run_minify_parser(
            source.before, target_python_version=version
        )
        assert python_code_is_valid(minified_function)
        assert expected == minified_function


def run_minifiyer_and_assert_correct(source: BeforeAndAfter):
    minified_function: str = run_minify_parser(source.before)
    assert python_code_is_valid(minified_function)
    assert source.after == minified_function


def python_code_is_valid(python_code: str) -> bool:
    try:
        ast.parse(python_code)
    except SyntaxError:
        return False

    return True


def _python_version_str_to_int_tuple(python_version: str) -> tuple[int, int]:
    return tuple(int(i) for i in python_version.split("."))[:2]
