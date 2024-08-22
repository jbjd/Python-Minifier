import pytest
from personal_python_minifier.parser import MinifyUnparser

from tests.utils import BeforeAndAfter, BeforeAndAfterBasedOnVersion


@pytest.fixture
def parser() -> MinifyUnparser:
    return MinifyUnparser()


@pytest.fixture
def dangling_constants_function() -> BeforeAndAfter:
    return BeforeAndAfter(
        """
def foo(bar: str) -> None:
    '''Some Doc String'''

    3  # This is some dangling constant
    a: int
    return "Hello World"
""",
        """
def foo(bar):return 'Hello World'
""".strip(),
    )


@pytest.fixture
def many_args_function() -> BeforeAndAfter:
    return BeforeAndAfter(
        """
def foo(bar, spam, eggs):
    a: int = 1
    return a
""",
        """
def foo(bar,spam,eggs):
\ta=1
\treturn a
""".strip(),
    )


@pytest.fixture
def dangling_constants_class() -> BeforeAndAfter:
    return BeforeAndAfter(
        """
class SomeClass:
    '''has a docstring'''
    def foo(bar):
        pass

    123
""",
        """
class SomeClass:
\tdef foo(bar):pass
""".strip(),
    )


@pytest.fixture
def only_docstring_class() -> BeforeAndAfter:
    return BeforeAndAfter(
        """
class Foo():
    '''Some Class'''
""",
        """
class Foo:pass
""".strip(),
    )


@pytest.fixture
def tuple_class() -> BeforeAndAfter:
    """Can't break annotations on tuple classes"""
    return BeforeAndAfter(
        """
class SomeTuple():
    '''A tuple, wow!'''
    thing1: str
    thing2: int
""",
        """
class SomeTuple:
\tthing1:'Any'
\tthing2:'Any'
""".strip(),
    )


@pytest.fixture
def ignorable_bases_class() -> BeforeAndAfterBasedOnVersion:
    return BeforeAndAfterBasedOnVersion(
        """
class Foo(object):
    pass
""",
        {"3.0": "class Foo:pass", None: "class Foo(object):pass"},
    )


@pytest.fixture
def annotations_script() -> BeforeAndAfter:
    return BeforeAndAfter("a: int;b: int = 2;b -= 1", "b=2\nb-=1")


@pytest.fixture
def one_line_if_script() -> BeforeAndAfter:
    return BeforeAndAfter(
        """
a if True else b
'a' if 'True' == 'False' else 'b'
""",
        """
a if True else b
'a'if 'True'=='False'else 'b'
""".strip(),
    )


@pytest.fixture
def futures_imports() -> BeforeAndAfterBasedOnVersion:
    many_futures_imports: str = """
from __future__ import annotations
from __future__ import generator_stop
from __future__ import unicode_literals
from __future__ import with_statement
"""
    return BeforeAndAfterBasedOnVersion(
        many_futures_imports,
        {"3.7": "", None: many_futures_imports.strip()},
    )


@pytest.fixture
def name_equals_main_excludes() -> BeforeAndAfter:
    return BeforeAndAfter(
        """
if __name__ == "__main__":
    a = 2
else:
    a = 1
""",
        "a=1",
    )
