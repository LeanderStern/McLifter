from base_model import MMUBaseModel
from mods_dependency_checker.enums.file_type_enum import FileTypeEnum

class FilesResponse(MMUBaseModel):
    hashes: dict[str, str]
    url: str
    filename: str
    primary: bool
    size: int
    file_type: FileTypeEnum | None = None