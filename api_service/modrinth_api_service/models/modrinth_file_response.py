from pathlib import Path
from typing import Annotated
from pydantic import Field, field_validator, AnyHttpUrl, NewPath
from base_model import MCLBaseModel
from api_service.modrinth_api_service.enums.modrinth_file_type_enum import ModrinthFileTypeEnum
from constraints import FilePath


class ModrinthFileResponse(MCLBaseModel):
    hashes: dict[str, str] = Field(description="The key is the hashing algorithm and the value is the string version of the hash.")
    url: AnyHttpUrl = Field(strict=False)
    filename: NewPath = Field(strict=False)
    primary: bool
    size: int = Field(gt=0)
    file_type: ModrinthFileTypeEnum | None = None

    @field_validator("filename")
    @classmethod
    def validate_jar(cls, value: NewPath) -> NewPath:
        if value.suffix != ".jar":
            raise ValueError("filename must end with .jar")
        return value