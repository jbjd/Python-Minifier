from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_exclude_name_equals_main(name_equals_main_excludes: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        name_equals_main_excludes, skip_name_equals_main=True
    )


def test_exclude_asserts(assert_excludes: BeforeAndAfter):
    run_minifiyer_and_assert_correct(assert_excludes, skip_asserts=True)
