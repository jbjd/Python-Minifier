from types import MethodType
from typing import Callable

from personal_python_syntax_optimizer.parser.config import (
    SectionsToSkipConfig,
    TokensToSkipConfig,
)
from personal_python_syntax_optimizer.parser.exclusion_decorators import (
    skip_class,
    skip_decorators,
    skip_dict_keys,
    skip_func_assign,
    skip_func_call,
    skip_func_def,
    skip_if_name_main,
    skip_import_from,
    skip_var_ann_assign,
    skip_var_assign,
    visit_decorator,
)
from personal_python_syntax_optimizer.parser.minifier import MinifyUnparser
from personal_python_syntax_optimizer.parser.utils import TokensToSkip


class ExclusionMinifierFactory:
    """Decorates a MinifierUnparser object with functions to exlcude bits of code"""

    __slots__ = ()

    # TODO: Refactor and test
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
            unparser.visit_If = make_method(skip_if_name_main(unparser.visit_If))

        if not tokens_config.has_code_to_skip():
            return unparser

        unparser.visit = make_method(visit_decorator(unparser.visit, tokens_config))

        tokens_to_skip: TokensToSkip
        for tokens_to_skip in tokens_config:
            if not tokens_to_skip:
                continue

            funcs_to_replace: list[tuple[str, Callable]] = {  # type: ignore
                "decorators": [("_write_decorators", skip_decorators)],
                "dict keys": [("visit_Dict", skip_dict_keys)],
                "classes": [("visit_ClassDef", skip_class)],
                "from imports": [("visit_ImportFrom", skip_import_from)],
                "functions": [
                    ("_function_helper", skip_func_def),
                    ("visit_Assign", skip_func_assign),
                    ("visit_Call", skip_func_call),
                ],
                "variables": [
                    ("visit_AnnAssign", skip_var_ann_assign),
                    ("visit_Assign", skip_var_assign),
                ],
            }.get(tokens_to_skip.token_type)

            for function_name, new_function in funcs_to_replace:

                new_method = make_method(
                    new_function(getattr(unparser, function_name), tokens_to_skip)
                )

                setattr(unparser, function_name, new_method)

        return unparser
