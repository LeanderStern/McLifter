from datetime import datetime
from typing import List

from pydantic import Field

from api_service.models.version_response import VersionResponse
from constraints import Base62Str, SemanticVersion, MinecraftVersion
from api_service.modrinth_api_service.enums.modrinth_requested_status_enum import ModrinthRequestedStatusEnum
from api_service.modrinth_api_service.enums.modrinth_status_enum import ModrinthStatusEnum
from api_service.modrinth_api_service.enums.modrinth_version_type_enum import ModrinthVersionTypeEnum
from api_service.modrinth_api_service.models.modrinth_dependencies_response import ModrinthDependenciesResponse
from api_service.modrinth_api_service.models.modrinth_file_response import ModrinthFileResponse

class ModrinthVersionResponse(VersionResponse):
    id: Base62Str
    project_id: Base62Str
    author_id: Base62Str
    date_published: datetime = Field(strict=False)
    downloads: int = Field(gt=0)
    files: List[ModrinthFileResponse] = Field(min_length=1)
    name: str | None = None
    version_number: SemanticVersion | None = None
    changelog: str | None = None
    dependencies: List[ModrinthDependenciesResponse] | None = None
    game_versions: List[str] | None = Field(default=None, min_length=1)
    version_type: ModrinthVersionTypeEnum | None = Field(default=None, strict=False)
    loaders: List[str] | None = None
    featured: bool | None = None
    status: ModrinthStatusEnum | None = Field(default=None, strict=False)
    requested_status: ModrinthRequestedStatusEnum | None = Field(default=None, strict=False)
