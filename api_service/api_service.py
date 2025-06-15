from abc import ABC, abstractmethod
from typing import List

from pydantic import validate_call

from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from constraints import MinecraftVersion, SemanticVersion


class ApiService(MCLBaseModel, ABC):

    @abstractmethod
    @validate_call
    def get_all_project_versions(self, project_slug, mod_loader, minecraft_version: SemanticVersion) -> List[VersionResponse]:
        pass

    @abstractmethod
    @validate_call
    def get_version(self, version_id) -> VersionResponse:
        pass