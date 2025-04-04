import ast
from typing import NamedTuple

from personal_python_ast_optimizer.factories.minifier_factory import (
    ExclusionMinifierFactory,
)
from personal_python_ast_optimizer.parser import run_minify_parser
from personal_python_ast_optimizer.parser.minifier import MinifyUnparser


class BeforeAndAfter(NamedTuple):
    """Input and output after minifiying it"""

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

        version_specific_source = BeforeAndAfter(source.before, expected)

        run_minifiyer_and_assert_correct(
            version_specific_source, target_python_version=version
        )


def run_minifiyer_and_assert_correct(
    source: BeforeAndAfter,
    target_python_version: tuple[int, int] | None = None,
    **kwargs,
):
    unparser: MinifyUnparser = MinifyUnparser(
        target_python_version=target_python_version
    )
    if kwargs:
        unparser = ExclusionMinifierFactory.create_minify_unparser_with_exclusions(
            unparser, **kwargs
        )

    minified_code: str = run_minify_parser(unparser, source.before)
    assert python_code_is_valid(minified_code)
    assert source.after == minified_code


def python_code_is_valid(python_code: str) -> bool:
    try:
        ast.parse(python_code)
        return True
    except SyntaxError:
        return False


def _python_version_str_to_int_tuple(python_version: str) -> tuple[int, int]:
    return tuple(int(i) for i in python_version.split("."))[:2]
