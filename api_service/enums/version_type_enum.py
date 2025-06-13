from enum import Enum

class VersionTypeEnum(Enum):
    RELEASE = (1, "release")
    BETA = (2, "beta")
    ALPHA = (3, "alpha")