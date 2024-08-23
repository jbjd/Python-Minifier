from dataclasses import dataclass


@dataclass
class ExcludeConfig:
    skip_asserts: bool = False
    skip_name_equals_main: bool = False
