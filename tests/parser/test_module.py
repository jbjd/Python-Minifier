from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_empty():
    before_and_after = BeforeAndAfter("", "")
    run_minifiyer_and_assert_correct(before_and_after)


def test_script_with_annotations():
    before_and_after = BeforeAndAfter("a: int;b: int = 2;b -= 1", "b=2\nb-=1")
    run_minifiyer_and_assert_correct(before_and_after)


def test_one_line_if():
    before_and_after = BeforeAndAfter(
        """
a if True else b
'a' if 'True' == 'False' else 'b'
""",
        """
a if True else b
'a'if 'True'=='False'else 'b'
""".strip(),
    )
    run_minifiyer_and_assert_correct(before_and_after)


def test_module_doc_string():
    before_and_after = BeforeAndAfter(
        """\"\"\"some doc string\"\"\"
foo = 5
""",
        "foo=5",
    )
    run_minifiyer_and_assert_correct(before_and_after)


def test_same_line_writing():
    before_and_after = BeforeAndAfter(
        """
for i in range(6):
    foo = 5
    pass
    continue
    break
    raise Exception
    bar = 2
""",
        "for i in range(6):foo=5;pass;continue;break;raise Exception;bar=2",
    )
    run_minifiyer_and_assert_correct(before_and_after)
