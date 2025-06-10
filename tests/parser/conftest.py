import pytest

from tests.utils import BeforeAndAfter


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
def many_returns_function() -> BeforeAndAfter:
    return BeforeAndAfter(
        """
def foo(bar):
    if bar:
        return None
    return 1
""",
        """
def foo(bar):
\tif bar:return
\treturn 1
""".strip(),
    )
