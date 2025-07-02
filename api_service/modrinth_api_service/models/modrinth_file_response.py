from pydantic import Field, AnyHttpUrl, model_serializer

from api_service.modrinth_api_service.enums.modrinth_file_type_enum import ModrinthFileTypeEnum
from api_service.modrinth_api_service.models.modrinth_hash_response import ModrinthHashResponse
from base_model import MCLBaseModel
from constraints import JarFile


class ModrinthFileResponse(MCLBaseModel):
    hashes: ModrinthHashResponse
    url: AnyHttpUrl = Field(strict=False)
    filename: JarFile
    primary: bool = Field(exclude=True)
    size: int = Field(exclude=True)
    file_type: ModrinthFileTypeEnum | None = Field(default=None, exclude=True)

    @model_serializer
    def serialize_model(self):
        return {
            "hash": self.hashes.sha512,
            "hash_algorithm": "sha512",
            "url": self.url,
            "filename": self.filename,
            "primary": self.primary,
            "size": self.size,
            "file_type": self.file_type.value if self.file_type else None
        }
