from abc import ABC, abstractmethod
from typing import Any

from pydantic import validate_call

from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from constraints import SemanticVersion


class ApiService(MCLBaseModel, ABC):
    mod_loader: Any
    minecraft_version: SemanticVersion

    @abstractmethod
    @validate_call
    def get_project_version(self, project_slug) -> VersionResponse | None:
        pass

    @abstractmethod
    @validate_call
    def get_version(self, version_id) -> VersionResponse:
        pass