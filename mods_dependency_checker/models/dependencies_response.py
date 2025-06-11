from dataclasses import dataclass
from typing import Optional

from mods_dependency_checker.enums.dependency_type_enum import DependencyTypeEnum


@dataclass()
class DependenciesResponse:
    dependency_type: DependencyTypeEnum
    version_id: Optional[str | None] = None
    project_id: Optional[str | None] = None
    file_name: Optional[str | None] = None