import pytest

from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


@pytest.mark.parametrize(
    "before_and_after",
    [
        (
            BeforeAndAfter(
                """
from foo import FAVORITE_NUMBER

a = FAVORITE_NUMBER
""",
                "a=6",
            )
        ),
        (
            BeforeAndAfter(
                """
FAVORITE_NUMBER = 6

a = FAVORITE_NUMBER
""",
                "a=6",
            )
        ),
        (
            BeforeAndAfter(
                """
FAVORITE_NUMBER: int = 6

a = FAVORITE_NUMBER
""",
                "a=6",
            )
        ),
        (
            BeforeAndAfter(
                """
FAVORITE_NUMBER = 5

a = FAVORITE_NUMBER
""",
                """
FAVORITE_NUMBER = 5
a=6
""".strip(),
            )
        ),
    ],
)
def test_exclude_name_equals_main(before_and_after: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        before_and_after,
        constant_vars_to_fold={"FAVORITE_NUMBER": 6},
    )
