import re
from typing import Iterable
import warnings

from personal_python_minifier.regex import RegexReplacement


def apply_regex(
    source: str,
    regex_replacement: RegexReplacement | Iterable[RegexReplacement],
    warning_id: str = "",
) -> str:
    """Runs a series of regex on given source.
    Passing warning_id enabled warnings when patterns are not found"""
    if isinstance(regex_replacement, RegexReplacement):
        regex_replacement = (regex_replacement,)

    for regex, replacement, flags, count in regex_replacement:
        source, count_replaced = re.subn(
            regex, replacement, source, flags=flags, count=count
        )
        if count_replaced == 0 and warning_id != "":
            warnings.warn(f"{warning_id}: Unused regex {regex}")

    return source


def apply_regex_to_file(
    path: str,
    regex_replacement: RegexReplacement | Iterable[RegexReplacement],
    warning_id: str = "",
):
    """Wraps apply_regex with opening and writing to a file"""
    with open(path) as fp:
        source: str = fp.read()

    source = apply_regex(source, regex_replacement, warning_id)

    with open(path, "w") as fp:
        fp.write(source)
