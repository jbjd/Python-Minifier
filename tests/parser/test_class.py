from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correctness


def test_function_with_many_args(only_docstring_class: BeforeAndAfter):
    run_minifiyer_and_assert_correctness(only_docstring_class)
