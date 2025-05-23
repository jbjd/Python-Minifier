from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_continue_same_line():
    before_and_after = BeforeAndAfter(
        """
if a > 6:
    raise Exception()
""",
        "if a>6:raise Exception()",
    )

    run_minifiyer_and_assert_correct(before_and_after)
