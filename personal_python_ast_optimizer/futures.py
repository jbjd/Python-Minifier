futures_to_mandatory_version: dict[str, tuple[int, int]] = {
    "nested_scopes": (2, 2),
    "generators": (2, 3),
    "with_statement": (2, 6),
    "division": (3, 0),
    "absolute_import": (3, 0),
    "print_function": (3, 0),
    "unicode_literals": (3, 0),
    "generator_stop": (3, 7),
}


def get_unneeded_futures(python_version: tuple[int, int]) -> list[str]:
    """Returns list of __future__ imports that are unneeded in provided
    python version"""
    unneeded_futures: list[str] = [
        future
        for future, mandatory_version in futures_to_mandatory_version.items()
        if python_version >= mandatory_version
    ]

    return unneeded_futures
