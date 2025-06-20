from datetime import datetime
from typing import List

from pydantic import Field, field_validator, TypeAdapter, field_serializer

from api_service.models.file_response import FileResponse
from api_service.modrinth_api_service.enums.modrinth_requested_status_enum import ModrinthRequestedStatusEnum
from api_service.modrinth_api_service.enums.modrinth_status_enum import ModrinthStatusEnum
from api_service.modrinth_api_service.enums.modrinth_version_type_enum import ModrinthVersionTypeEnum
from api_service.modrinth_api_service.models.modrinth_dependencies_response import ModrinthDependenciesResponse
from api_service.modrinth_api_service.models.modrinth_file_response import ModrinthFileResponse
from base_model import MCLBaseModel
from constraints import Base62Str, SemanticVersion, NotEmptyList


class ModrinthVersionResponse(MCLBaseModel):
    id: Base62Str
    project_id: Base62Str
    author_id: Base62Str
    date_published: datetime = Field(strict=False)
    downloads: int
    files: NotEmptyList[ModrinthFileResponse] = Field(serialization_alias="file")
    name: str | None = None
    version_number: SemanticVersion | None = None
    changelog: str | None = None
    dependencies: List[ModrinthDependenciesResponse] | None = None
    game_versions: NotEmptyList[str] | None = None
    version_type: ModrinthVersionTypeEnum | None = Field(default=None, strict=False)
    loaders: List[str] | None = None
    featured: bool | None = None
    status: ModrinthStatusEnum | None = Field(default=None, strict=False)
    requested_status: ModrinthRequestedStatusEnum | None = Field(default=None, strict=False)

    @field_validator("version_number", mode="plain")
    @classmethod
    def validate_version_number(cls, value) -> SemanticVersion | None:
        try:
            return TypeAdapter(SemanticVersion).validate_python(value)
        except ValueError:
            return None

    @field_serializer("files")
    def serialize_files(self, value: NotEmptyList[ModrinthFileResponse]):
        if len(value) == 1:
            return value[0].model_dump()
        else:
            primary_version: ModrinthVersionResponse | None = next(filter(lambda x: x.primary, value), None)
            if primary_version:
                return primary_version.model_dump()
            else:
                raise ValueError("No primary file found in the version files which should never happen.")