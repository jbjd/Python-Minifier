from minifier.parser import run_minify_parser
from tests.utils import BeforeAndAfter


def test_default_function_minifiy(example_function: BeforeAndAfter):
    minified_function: str = run_minify_parser(example_function.before)
    assert minified_function == example_function.after
