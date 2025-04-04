from typing import Iterator

from personal_python_ast_optimizer.parser.utils import TokensToSkip


class TokensToSkipConfig:

    __slots__ = (
        "from_imports",
        "functions",
        "variables",
        "classes",
        "dict_keys",
        "decorators",
        "no_warn",
    )

    TOKEN_ATTRS = (
        "from_imports",
        "functions",
        "variables",
        "classes",
        "dict_keys",
        "decorators",
    )

    def __init__(
        self,
        from_imports: set[str] | None = None,
        functions: set[str] | None = None,
        variables: set[str] | None = None,
        classes: set[str] | None = None,
        dict_keys: set[str] | None = None,
        decorators: set[str] | None = None,
        no_warn: set[str] | None = None,
    ):
        self.from_imports = TokensToSkip(from_imports, "from imports")
        self.functions = TokensToSkip(functions, "functions")
        self.variables = TokensToSkip(variables, "variables")
        self.classes = TokensToSkip(classes, "classes")
        self.dict_keys = TokensToSkip(dict_keys, "dict keys")
        self.decorators = TokensToSkip(decorators, "decorators")
        self.no_warn: set[str] = no_warn if no_warn is not None else set()

    def __iter__(self) -> Iterator[TokensToSkip]:
        for attr in self.TOKEN_ATTRS:
            yield getattr(self, attr)

    def has_code_to_skip(self) -> bool:
        return any(self)  # type: ignore


class SectionsToSkipConfig:
    __slots__ = ("skip_name_equals_main",)

    def __init__(self, skip_name_equals_main: bool = False) -> None:
        self.skip_name_equals_main: bool = skip_name_equals_main

    def has_code_to_skip(self) -> bool:
        return any(getattr(self, attr) for attr in self.__slots__)
