from abc import ABC, abstractmethod
from typing import Any

from pydantic import validate_call, AnyHttpUrl

from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from constraints import SemanticVersion, DirectoryPath


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

    @abstractmethod
    @validate_call
    def download_version(self, path_to_dir: DirectoryPath, download_link: AnyHttpUrl) -> None:
        pass