from pydantic import FileUrl

from base_model import MCLBaseModel
from api_service.modrinth_api_service.enums.file_type_enum import FileTypeEnum

class ModrinthFileResponse(MCLBaseModel):
    hashes: dict[str, str]
    url: FileUrl
    filename: str
    primary: bool
    size: int
    file_type: FileTypeEnum | None = None