from enum import Enum, StrEnum


class ModrinthStatusEnum(StrEnum):
    LISTED = "listed"
    ARCHIVED = "archived"
    DRAFT = "draft"
    UNLISTED = "unlisted"
    SCHEDULED = "scheduled"
    UNKNOWN = "unknown"