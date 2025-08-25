from abc import ABC, abstractmethod

from pydantic import validate_call, AnyHttpUrl

from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from constraints import SemanticVersion, DirectoryPath


class ApiService(MCLBaseModel, ABC):

    @abstractmethod
    @validate_call
    def get_project_version(self, project_slug, minecraft_version: SemanticVersion | None) -> VersionResponse | None:
        """if minecraft_version is None, the function returns the most recent version"""

    @abstractmethod
    @validate_call
    def get_version(self, version_id) -> VersionResponse:
        pass

    @abstractmethod
    @validate_call
    def download_version(self, path_to_dir: DirectoryPath,
                         download_link: AnyHttpUrl,
                         hash_value: str | None = None,
                         hash_algorithm: str | None = None) -> None:
        pass
