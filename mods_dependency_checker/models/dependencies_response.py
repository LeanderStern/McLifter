from base_model import MMUBaseModel
from mods_dependency_checker.enums.dependency_type_enum import DependencyTypeEnum


class DependenciesResponse(MMUBaseModel):
    dependency_type: DependencyTypeEnum
    version_id: str | None = None
    project_id: str | None = None
    file_name: str | None = None