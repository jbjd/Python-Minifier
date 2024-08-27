from types import MethodType
from typing import Callable

from personal_python_minifier.parser.config import (
    TokensToSkipConfig,
    SectionsToSkipConfig,
)
from personal_python_minifier.parser.exclusion_decorators import (
    visit_ClassDef_decorator,
    visit_Dict_decorator,
    visit_If_decorator,
    visit_ImportFrom_decorator,
    visit_decorator,
)
from personal_python_minifier.parser.minifier import MinifyUnparser
from personal_python_minifier.parser.utils import TokensToSkip


class ExclusionMinifierFactory:
    """Creates a MinifierUnparser object with decorated functions
    to exlcude bits of code"""

    __slots__ = ()

    # TODO: Refactor
    @staticmethod
    def create_minify_unparser_with_exclusions(
        unparser: MinifyUnparser,
        sections_config: SectionsToSkipConfig = SectionsToSkipConfig(),
        tokens_config: TokensToSkipConfig = TokensToSkipConfig(),
    ) -> MinifyUnparser:
        if (
            not tokens_config.has_code_to_skip()
            and not sections_config.has_code_to_skip()
        ):
            return unparser

        make_method = lambda func: MethodType(func, unparser)  # noqa E731

        if sections_config.skip_name_equals_main:
            unparser.visit_If = make_method(visit_If_decorator(unparser.visit_If))

        if not tokens_config.has_code_to_skip():
            return unparser

        unparser.visit = make_method(visit_decorator(unparser.visit, tokens_config))

        tokens_to_skip: TokensToSkip
        for tokens_to_skip in tokens_config:
            if not tokens_to_skip:
                continue

            funcs_to_replace: list[tuple[str, Callable]] = {
                "dict keys": [("visit_Dict", visit_Dict_decorator)],
                "classes": [("visit_ClassDef", visit_ClassDef_decorator)],
                "from imports": [("visit_ImportFrom", visit_ImportFrom_decorator)],
                "functions": [],  # TODO
                "vars": [],
            }.get(tokens_to_skip.token_type)

            for function_name, new_function in funcs_to_replace:

                new_method = make_method(
                    new_function(getattr(unparser, function_name), tokens_to_skip)
                )

                setattr(unparser, function_name, new_method)

        return unparser
