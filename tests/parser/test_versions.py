"""Optimizations that should only be used on a specific version"""

from tests.utils import (
    BeforeAndAfterBasedOnVersion,
    run_minifiyer_and_assert_correct_multiple_versions,
)


def test_class_ignorable_bases(ignorable_bases_class: BeforeAndAfterBasedOnVersion):
    run_minifiyer_and_assert_correct_multiple_versions(ignorable_bases_class)
