from enum import Enum, StrEnum


class ModrinthRequestedStatusEnum(StrEnum):
    LISTED = "listed"
    ARCHIVED = "archived"
    DRAFT = "draft"
    UNLISTED = "unlisted"