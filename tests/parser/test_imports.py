from tests.utils import (
    BeforeAndAfterBasedOnVersion,
    run_minifiyer_and_assert_correct_multiple_versions,
)


def test_futures_imports():

    many_futures_imports: str = """
from __future__ import annotations
from __future__ import generator_stop
from __future__ import unicode_literals
from __future__ import with_statement
"""

    before_and_after = BeforeAndAfterBasedOnVersion(
        many_futures_imports,
        {"3.7": "", None: many_futures_imports.strip()},
    )

    run_minifiyer_and_assert_correct_multiple_versions(before_and_after)
