from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_empty():
    empty_script = BeforeAndAfter("", "")
    run_minifiyer_and_assert_correct(empty_script)


def test_script_with_annotations(annotations_script: BeforeAndAfter):
    run_minifiyer_and_assert_correct(annotations_script)
