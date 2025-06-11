from enum import Enum

class RequestedStatusEnum(Enum):
    LISTED = "listed"
    ARCHIVED = "archived"
    DRAFT = "draft"
    UNLISTED = "unlisted"