import pytest

from tests.utils import BeforeAndAfter


@pytest.fixture
def dangling_constants_function() -> str:
    return BeforeAndAfter(
        """
def foo(bar: str) -> None:
    '''Some Doc String'''

    3  # This is some dangling constant
    return "Hello World"
""",
        """
def foo(bar):
\treturn 'Hello World'
""".strip(),
    )


@pytest.fixture
def only_docstring_function() -> str:
    return BeforeAndAfter(
        """
def foo(bar):
    '''Some Doc String'''

print()
""",
        """
def foo(bar):pass
print()
""".strip(),
    )
