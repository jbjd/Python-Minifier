from tests.utils import (
    BeforeAndAfterBasedOnVersion,
    run_minifiyer_and_assert_correct_multiple_versions,
)


def test_futures_imports(
    futures_imports: BeforeAndAfterBasedOnVersion,
):
    run_minifiyer_and_assert_correct_multiple_versions(futures_imports)
