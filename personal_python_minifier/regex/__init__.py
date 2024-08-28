from dataclasses import dataclass
from typing import Iterator


@dataclass(repr=False, eq=False, slots=True)
class RegexReplacement:
    pattern: str
    replacement: str = ""
    flags: int = 0
    count: int = 0

    def __iter__(self) -> Iterator:
        return iter((self.pattern, self.replacement, self.flags, self.count))
