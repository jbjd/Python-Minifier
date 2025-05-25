import autoflake


def run_autoflake(source: str, remove_unused_imports: bool = False) -> str:
    """Runs autoflake
    remove_unused_imports: defaults to False since it can be destructive
        Some module (foo) import what another module (bar) imported and this can remove
        If module "bar" does not use the imports itself, autoflake will remove it
    """
    return autoflake.fix_code(
        source,
        remove_all_unused_imports=remove_unused_imports,
        remove_duplicate_keys=True,
        remove_unused_variables=True,
        remove_rhs_for_unused_variables=True,
    )
