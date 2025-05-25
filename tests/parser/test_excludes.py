import pytest
from personal_python_ast_optimizer.parser.config import (
    SectionsToSkipConfig,
    TokensToSkipConfig,
)

from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_exclude_name_equals_main(name_equals_main_excludes: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        name_equals_main_excludes,
        sections_config=SectionsToSkipConfig(skip_name_equals_main=True),
    )


def test_exclude_classes(class_excludes: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        class_excludes,
        tokens_config=TokensToSkipConfig(classes={"ABC", "B"}),
    )


_exclude_assign_cases = [
    BeforeAndAfter(
        """
a = 1
foo = 2
""",
        "a=1",
    ),
    BeforeAndAfter(
        """
def bar():
    foo = 2
""",
        "def bar():pass",
    ),
    BeforeAndAfter(
        """
def bar():
    test = 1
    foo = 2
""",
        "def bar():test=1",
    ),
    BeforeAndAfter(
        """
def bar():
    foo = 2
    test = 1
""",
        "def bar():pass;test=1",
    ),
]


@pytest.mark.parametrize("before_and_after", _exclude_assign_cases)
def test_exclude_assign(before_and_after: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        before_and_after,
        tokens_config=TokensToSkipConfig(variables={"foo"}),
    )


_exclude_function_def_cases = [
    BeforeAndAfter(
        """
def foo():
    pass
""",
        "",
    ),
    BeforeAndAfter(
        """
def bar():
    def foo():
        pass
""",
        "def bar():\n\tpass",
    ),
]


@pytest.mark.parametrize("before_and_after", _exclude_function_def_cases)
def test_exclude_function_def(before_and_after: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        before_and_after,
        tokens_config=TokensToSkipConfig(functions={"foo"}),
    )


_exclude_function_call_cases = [
    BeforeAndAfter(
        """
foo()
""",
        "",
    ),
    BeforeAndAfter(
        """
def bar():
    a=0
    foo()
test=1
""",
        "def bar():\n\ta=0\ntest=1",
    ),
]


@pytest.mark.parametrize("before_and_after", _exclude_function_call_cases)
def test_exclude_function_call(before_and_after: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        before_and_after,
        tokens_config=TokensToSkipConfig(functions={"foo"}),
    )


_exclude_function_assign_cases = [
    BeforeAndAfter(
        """
a=foo()
""",
        "",
    ),
    BeforeAndAfter(
        """
def bar():
    a=foo()
""",
        "def bar():pass",
    ),
]


@pytest.mark.parametrize("before_and_after", _exclude_function_assign_cases)
def test_exclude_function_assign(before_and_after: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        before_and_after,
        tokens_config=TokensToSkipConfig(functions={"foo"}),
    )


def test_exclude_real_case():
    before_and_after = BeforeAndAfter(
        """
from ._util import DeferredError

TYPE_CHECKING = False

logger = logging.getLogger(__name__)

is_cid = re.compile('').match
""",
        "from ._util import DeferredError\nis_cid=re.compile('').match",
    )
    run_minifiyer_and_assert_correct(
        before_and_after,
        tokens_config=TokensToSkipConfig(
            functions={"getLogger"}, variables={"TYPE_CHECKING"}
        ),
    )
