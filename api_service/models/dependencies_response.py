from typing import Any

from api_service.enums.dependency_type_enum import DependencyTypeEnum
from base_model import MCLBaseModel


class DependenciesResponse(MCLBaseModel):
    version_id: Any
    project_id: Any
    dependency_type: DependencyTypeEnum