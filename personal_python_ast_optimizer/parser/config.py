from abc import ABC, abstractmethod
from typing import Iterator


class TokensToSkip(dict[str, int]):

    __slots__ = ("_tokens_to_skip", "token_type")

    def __init__(self, tokens_to_skip: set[str] | None, token_type: str) -> None:
        tokens_to_skip: dict[str, int] = self._set_to_dict_of_counts(tokens_to_skip)
        super().__init__(tokens_to_skip)

        self.token_type: str = token_type

    def __contains__(self, key: str) -> bool:
        """Returns if token is marked to skip and
        increments internal counter when True is returned"""
        contains: bool = super().__contains__(key)

        if contains:
            self[key] += 1

        return contains

    def get_not_found_tokens(self) -> set[str]:
        return set(token for token, found_count in self.items() if found_count == 0)

    @staticmethod
    def _set_to_dict_of_counts(input_set: set[str] | None) -> dict[str, int]:
        if not input_set:
            return {}

        return {key: 0 for key in input_set}


class Config(ABC):

    __slots__ = ()

    @abstractmethod
    def has_code_to_skip(self) -> bool:
        pass


class TokensToSkipConfig(Config):

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


class SectionsToSkipConfig(Config):
    __slots__ = ("skip_name_equals_main",)

    def __init__(self, skip_name_equals_main: bool = False) -> None:
        self.skip_name_equals_main: bool = skip_name_equals_main

    def has_code_to_skip(self) -> bool:
        return any(getattr(self, attr) for attr in self.__slots__)


class SkipConfig(Config):

    __slots__ = (
        "module_name",
        "skip_type_hints",
        "target_python_version",
        "constant_vars_to_fold",
        "sections_to_skip_config",
        "tokens_to_skip_config",
    )

    def __init__(
        self,
        module_name: str = "",
        skip_type_hints: bool = False,
        target_python_version: tuple[int, int] | None = None,
        constant_vars_to_fold: dict[str, int | str] | None = None,
        sections_to_skip_config: SectionsToSkipConfig = SectionsToSkipConfig(),
        tokens_to_skip_config: TokensToSkipConfig = TokensToSkipConfig(),
    ) -> None:
        self.module_name: str = module_name
        self.skip_type_hints: bool = skip_type_hints
        self.target_python_version: tuple[int, int] | None = target_python_version
        self.constant_vars_to_fold: dict[str, int | str] = (
            {} if constant_vars_to_fold is None else constant_vars_to_fold
        )
        self.sections_to_skip_config: SectionsToSkipConfig = sections_to_skip_config
        self.tokens_to_skip_config: TokensToSkipConfig = tokens_to_skip_config

    def has_code_to_skip(self) -> bool:
        return (
            self.skip_type_hints
            or self.target_python_version is not None
            or len(self.constant_vars_to_fold) > 0
            or self.sections_to_skip_config.has_code_to_skip()
            or self.tokens_to_skip_config.has_code_to_skip()
        )
