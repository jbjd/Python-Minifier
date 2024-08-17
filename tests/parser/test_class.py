from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_class_only_docstring(only_docstring_class: BeforeAndAfter):
    run_minifiyer_and_assert_correct(only_docstring_class)


def test_tuple_class(tuple_class: BeforeAndAfter):
    run_minifiyer_and_assert_correct(tuple_class)


def test_class_dangling_constants(tuple_class: BeforeAndAfter):
    run_minifiyer_and_assert_correct(tuple_class)
