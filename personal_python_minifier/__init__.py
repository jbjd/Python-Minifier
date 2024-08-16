from personal_python_minifier.flake_wrapper import run_autoflake
from personal_python_minifier.parser import run_minify_parser


def minify(source: str, remove_unused_imports: bool = False) -> str:
    """
    Minifies provided Python code

    remove_unused_imports: Removes imports if they are unused in the module itself.
        This may break code if you import the 'unused' import in another module"""
    source = run_minify_parser(source)
    source = run_autoflake(source, remove_unused_imports=remove_unused_imports)
    return source
