from enum import EnumMeta, StrEnum

class NoClassPropertyAccessEnumMeta(EnumMeta):
    def __getattribute__(cls, item):
        attr = super().__getattribute__(item)
        if isinstance(attr, property):
            raise AttributeError(
                f"Cannot access property '{item}' on the enum class itself. "
                "Use a member, e.g., RagebaitEnum.HEISSUNDFETTIG.rank"
            )
        return attr

class VersionTypeEnum(StrEnum, metaclass=NoClassPropertyAccessEnumMeta):
    RELEASE = "release"
    BETA = "beta"
    ALPHA = "alpha"

    @property
    def rank(self):
        match self.value:
            case self.RELEASE.value:
                return 1
            case self.BETA.value:
                return 2
            case self.ALPHA.value:
                return 3
            case _:
                raise ValueError(f"Unknown version type: {self.value}")