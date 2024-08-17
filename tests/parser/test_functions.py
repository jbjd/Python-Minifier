from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_function_dangling_constants(dangling_constants_function: BeforeAndAfter):
    run_minifiyer_and_assert_correct(dangling_constants_function)


def test_function_only_docstring(only_docstring_function: BeforeAndAfter):
    run_minifiyer_and_assert_correct(only_docstring_function)


def test_function_with_many_args(many_args_function: BeforeAndAfter):
    run_minifiyer_and_assert_correct(many_args_function)
