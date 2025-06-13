from pydantic import Field

from base_model import MCLBaseModel
from api_service.modrinth_api_service.enums.modrinth_dependency_type_enum import ModrinthDependencyTypeEnum
from constraints import Base62Str


class ModrinthDependenciesResponse(MCLBaseModel):
    dependency_type: ModrinthDependencyTypeEnum = Field(strict=False)
    version_id: Base62Str | None = None
    project_id: Base62Str | None = None
    file_name: str | None = None