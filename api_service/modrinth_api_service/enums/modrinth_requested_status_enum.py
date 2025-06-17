from enum import StrEnum


class ModrinthRequestedStatusEnum(StrEnum):
    LISTED = "listed"
    ARCHIVED = "archived"
    DRAFT = "draft"
    UNLISTED = "unlisted"