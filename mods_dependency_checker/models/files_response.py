from dataclasses import dataclass
from typing import Optional

from mods_dependency_checker.enums.file_type_enum import FileTypeEnum


@dataclass()
class FilesResponse:
    hashes: dict[str, str]
    url: str
    filename: str
    primary: bool
    size: int
    file_type: Optional[FileTypeEnum | None] = None