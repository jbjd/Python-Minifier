from minifier.parser import run_minify_parser
from tests.utils import BeforeAndAfter, is_python_code_valid


def test_dangling_constants_function(dangling_constants_function: BeforeAndAfter):
    minified_function: str = run_minify_parser(dangling_constants_function.before)
    assert minified_function == dangling_constants_function.after
    assert is_python_code_valid(minified_function)


def test_function_only_docstring(only_docstring_function: BeforeAndAfter):
    minified_function: str = run_minify_parser(only_docstring_function.before)
    assert minified_function == only_docstring_function.after
    assert is_python_code_valid(minified_function)
