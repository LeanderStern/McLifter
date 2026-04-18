from abc import abstractmethod, ABC
from typing import List

from api_service.api_service import ApiService
from base_model import MCLBaseModel
from constraints import NotEmptyList, SemanticVersion
from task_builder.models.download_task import DownloadTask


class Resolver(MCLBaseModel, ABC):
    api_service: ApiService
    version_to_update_to: SemanticVersion

    @abstractmethod
    def resolve_dependencies(self, tasks: NotEmptyList[DownloadTask]) -> List[DownloadTask]:
        """
        This method populates DownloadTask.dependency_versions with the versions of the dependencies that are required to resolve the task.
        The versions inside DownloadTask.dependency_versions are always unique inside their respective list of tasks.
        """