from pydantic import Field, AnyHttpUrl

from api_service.modrinth_api_service.enums.modrinth_file_type_enum import ModrinthFileTypeEnum
from base_model import MCLBaseModel
from constraints import JarFile


class ModrinthFileResponse(MCLBaseModel):
    hashes: dict[str, str] = Field(description="The key is the hashing algorithm and the value is the string version of the hash.")
    url: AnyHttpUrl = Field(strict=False)
    filename: JarFile
    primary: bool = Field(exclude=True)
    size: int = Field(gt=0, exclude=True)
    file_type: ModrinthFileTypeEnum | None = Field(default=None, exclude=True)
