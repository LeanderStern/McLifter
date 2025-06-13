from enum import Enum

class ModrinthRequestedStatusEnum(Enum):
    LISTED = "listed"
    ARCHIVED = "archived"
    DRAFT = "draft"
    UNLISTED = "unlisted"