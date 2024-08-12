import pytest

from tests.utils import BeforeAndAfter


@pytest.fixture
def example_function() -> str:
    return BeforeAndAfter(
        """
def foo(bar: str) -> None:
    '''Some Doc String'''

    3  # This is some dangling constant
    return "Hello World"
""",
        """
def foo(bar):
    return 'Hello World'
""".strip(),
    )
