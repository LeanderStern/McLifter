from datetime import datetime
from typing import List

from pydantic import Field

from api_service.models.get_version_response import GetVersionResponse
from constraints import Base62Str, SemanticVersion, MinecraftVersion
from api_service.modrinth_api_service.enums.requested_status_enum import RequestedStatusEnum
from api_service.modrinth_api_service.enums.status_enum import StatusEnum
from api_service.modrinth_api_service.enums.version_type_enum import VersionTypeEnum
from api_service.modrinth_api_service.models.modrinth_dependencies_response import ModrinthDependenciesResponse
from api_service.modrinth_api_service.models.modrinth_file_response import ModrinthFileResponse

class ModrinthVersionResponse(GetVersionResponse):
    id: Base62Str
    project_id: Base62Str
    author_id: Base62Str
    date_published: datetime = Field(strict=False)
    downloads: int = Field(gt=0)
    files: List[ModrinthFileResponse] = Field(min_length=1)
    name: str | None = None
    version_number: str | None = None
    changelog: str | None = None
    dependencies: List[ModrinthDependenciesResponse] | None = None
    game_versions: List[str] | None = Field(default=None, min_length=1)
    version_type: VersionTypeEnum | None = Field(default=None, strict=False)
    loaders: List[str] | None = None
    featured: bool | None = None
    status: StatusEnum | None = Field(default=None, strict=False)
    requested_status: RequestedStatusEnum | None = Field(default=None, strict=False)
