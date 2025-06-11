from datetime import datetime
from typing import List

from pydantic import Field

from base_model import MMUBaseModel
from constraints import Base62Str, SemanticVersion
from mods_dependency_checker.enums.requested_status_enum import RequestedStatusEnum
from mods_dependency_checker.enums.status_enum import StatusEnum
from mods_dependency_checker.enums.version_type_enum import VersionTypeEnum
from mods_dependency_checker.models.dependencies_response import DependenciesResponse
from mods_dependency_checker.models.files_response import FilesResponse

class VersionResponse(MMUBaseModel):
    id: Base62Str
    project_id: Base62Str
    author_id: Base62Str
    date_published: datetime = Field(strict=False)
    downloads: int
    files: List[FilesResponse] = Field(min_length=1)
    name: str | None = None
    version_number: str | None = None
    changelog: str | None = None
    dependencies: List[DependenciesResponse] | None = None
    game_versions: List[SemanticVersion] | None = Field(default=None, min_length=1)
    version_type: VersionTypeEnum | None = None
    loaders: List[str] | None = None
    featured: bool | None = None
    status: StatusEnum | None = None
    requested_status: RequestedStatusEnum | None = None
