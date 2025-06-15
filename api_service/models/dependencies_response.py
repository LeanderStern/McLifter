from typing import Any

from pydantic import Field

from api_service.enums.dependency_type_enum import DependencyTypeEnum
from base_model import MCLBaseModel


class DependenciesResponse(MCLBaseModel):
    dependency_type: DependencyTypeEnum = Field(strict=False)
    version_id: Any | None = None
    project_id: Any| None = None