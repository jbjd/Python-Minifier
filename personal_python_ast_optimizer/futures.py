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


def get_ignorable_futures(
    python_version: tuple[int, int], always_include_annotation: bool = True
) -> list[str]:
    ignorable_futures: list[str] = [
        future
        for future, mandatory_version in futures_to_mandatory_version.items()
        if python_version >= mandatory_version
    ]

    if always_include_annotation:
        ignorable_futures.append("annotations")

    return ignorable_futures
