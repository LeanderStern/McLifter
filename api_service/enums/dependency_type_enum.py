from enum import Enum


class DependencyTypeEnum(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    INCOMPATIBLE = "incompatible"