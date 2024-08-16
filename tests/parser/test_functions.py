from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correctness


def test_function_dangling_constants(dangling_constants_function: BeforeAndAfter):
    run_minifiyer_and_assert_correctness(dangling_constants_function)


def test_function_only_docstring(only_docstring_function: BeforeAndAfter):
    run_minifiyer_and_assert_correctness(only_docstring_function)


def test_function_with_many_args(many_args_function: BeforeAndAfter):
    run_minifiyer_and_assert_correctness(many_args_function)
