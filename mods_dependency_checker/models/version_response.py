from dataclasses import dataclass
from typing import Optional, List

from mods_dependency_checker.enums.requested_status_enum import RequestedStatusEnum
from mods_dependency_checker.enums.status_enum import StatusEnum
from mods_dependency_checker.enums.version_type_enum import VersionTypeEnum
from mods_dependency_checker.models.dependencies_response import DependenciesResponse
from mods_dependency_checker.models.files_response import FilesResponse


@dataclass()
class VersionResponse:
    id: str
    project_id: str
    author_id: str
    date_published: str
    downloads: int
    files: List[FilesResponse]
    name: Optional[str] = None
    version_number: Optional[str] = None
    changelog: Optional[str | None] = None
    dependencies: Optional[List[DependenciesResponse]] = None
    game_versions: Optional[List[str]] = None
    version_type: Optional[VersionTypeEnum] = None
    loaders: Optional[List[str]] = None
    featured: Optional[bool] = None
    status: Optional[StatusEnum] = None
    requested_status: Optional[RequestedStatusEnum | None] = None
