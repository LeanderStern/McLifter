from typing import List, Any

from pydantic import Field

from api_service.enums.version_type_enum import VersionTypeEnum
from api_service.models.dependencies_response import DependenciesResponse
from base_model import MCLBaseModel
from constraints import SemanticVersion


class VersionResponse(MCLBaseModel):
    id: Any
    project_id: Any
    dependencies: List[DependenciesResponse] | None = None
    version_number: SemanticVersion | None = None
    version_type: VersionTypeEnum | None = Field(default=None, strict=False)

    def __eq__(self, other: object) -> bool:
        match other:
            case str():
                return self.id == other
            case VersionResponse():
                return self.id == other.id
            case _:
                raise TypeError("Can only compare DownloadTask with DownloadTask")