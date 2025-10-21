from enum import Enum


def get_enum_values(enum_class: type[Enum]) -> list[str]:
    return [c.value for c in enum_class]
