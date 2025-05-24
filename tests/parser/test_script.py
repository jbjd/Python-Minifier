from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_empty():
    empty_script = BeforeAndAfter("", "")
    run_minifiyer_and_assert_correct(empty_script)


def test_script_with_annotations(annotations_script: BeforeAndAfter):
    run_minifiyer_and_assert_correct(annotations_script)


def test_one_line_if(one_line_if_script: BeforeAndAfter):
    run_minifiyer_and_assert_correct(one_line_if_script)


def test_module_doc_string():
    before_and_after = BeforeAndAfter(
        """\"\"\"some doc string\"\"\"
foo = 5
""",
        "foo=5",
    )
    run_minifiyer_and_assert_correct(before_and_after)
