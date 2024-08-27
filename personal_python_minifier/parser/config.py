from typing import Iterable
from personal_python_minifier.parser.utils import TokensToSkip


class TokensToSkipConfig:

    __slots__ = ("from_imports", "functions", "vars", "classes", "dict_keys")

    def __init__(
        self,
        from_imports: set[str] | None = None,
        functions: set[str] | None = None,
        vars: set[str] | None = None,
        classes: set[str] | None = None,
        dict_keys: set[str] | None = None,
    ):
        self.from_imports = TokensToSkip(from_imports, "from imports")
        self.functions = TokensToSkip(functions, "functions")
        self.vars = TokensToSkip(vars, "vars")
        self.classes = TokensToSkip(classes, "classes")
        self.dict_keys = TokensToSkip(dict_keys, "dict keys")

    def __iter__(self) -> Iterable[TokensToSkip]:
        for attr in self.__slots__:
            yield getattr(self, attr)

    def has_code_to_skip(self) -> bool:
        return any(getattr(self, attr) for attr in self.__slots__)


class SectionsToSkipConfig:
    __slots__ = ("skip_name_equals_main",)

    def __init__(self, skip_name_equals_main: bool = False) -> None:
        self.skip_name_equals_main: bool = skip_name_equals_main

    def has_code_to_skip(self) -> bool:
        return any(getattr(self, attr) for attr in self.__slots__)
