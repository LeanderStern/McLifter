from datetime import datetime
from typing import List

from pydantic import Field, field_validator, TypeAdapter

from api_service.models.version_response import VersionResponse
from api_service.modrinth_api_service.enums.modrinth_requested_status_enum import ModrinthRequestedStatusEnum
from api_service.modrinth_api_service.enums.modrinth_status_enum import ModrinthStatusEnum
from api_service.modrinth_api_service.enums.modrinth_version_type_enum import ModrinthVersionTypeEnum
from api_service.modrinth_api_service.models.modrinth_dependencies_response import ModrinthDependenciesResponse
from api_service.modrinth_api_service.models.modrinth_file_response import ModrinthFileResponse
from constraints import Base62Str, SemanticVersion, NotEmptyList


class ModrinthVersionResponse(VersionResponse):
    project_id: Base62Str
    author_id: Base62Str
    date_published: datetime = Field(strict=False)
    downloads: int
    files: NotEmptyList[ModrinthFileResponse]
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
            a = TypeAdapter(SemanticVersion).validate_python(value)
            return a
        except ValueError:
            return None
