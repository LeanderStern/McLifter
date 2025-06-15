from enum import Enum, StrEnum


class ModrinthDependencyTypeEnum(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    INCOMPATIBLE = "incompatible"
    EMBEDDED = "embedded"