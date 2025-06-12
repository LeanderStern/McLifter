from base_model import MCLBaseModel
from api_service.modrinth_api_service.enums.dependency_type_enum import DependencyTypeEnum


class ModrinthDependenciesResponse(MCLBaseModel):
    dependency_type: DependencyTypeEnum
    version_id: str | None = None
    project_id: str | None = None
    file_name: str | None = None