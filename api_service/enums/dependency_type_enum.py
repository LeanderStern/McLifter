from enum import StrEnum


class DependencyTypeEnum(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    INCOMPATIBLE = "incompatible"
    EMBEDDED = "embedded"