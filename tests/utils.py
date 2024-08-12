from typing import NamedTuple


class BeforeAndAfter(NamedTuple):
    """Input and what is expected after minifiying it"""

    before: str
    after: str
