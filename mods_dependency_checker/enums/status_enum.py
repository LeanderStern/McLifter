from enum import Enum

class StatusEnum(Enum):
    LISTED = "listed"
    ARCHIVED = "archived"
    DRAFT = "draft"
    UNLISTED = "unlisted"
    SCHEDULED = "scheduled"
    UNKNOWN = "unknown"