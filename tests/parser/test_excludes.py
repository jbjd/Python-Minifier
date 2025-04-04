from personal_python_ast_optimizer.parser.config import (
    SectionsToSkipConfig,
    TokensToSkipConfig,
)

from tests.utils import BeforeAndAfter, run_minifiyer_and_assert_correct


def test_exclude_name_equals_main(name_equals_main_excludes: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        name_equals_main_excludes,
        sections_config=SectionsToSkipConfig(skip_name_equals_main=True),
    )


def test_exclude_classes(class_excludes: BeforeAndAfter):
    run_minifiyer_and_assert_correct(
        class_excludes,
        tokens_config=TokensToSkipConfig(classes={"ABC", "B"}),
    )
