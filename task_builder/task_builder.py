from abc import abstractmethod, ABC
from typing import List

from base_model import MCLBaseModel
from constraints import NotEmptyList
from file_manager.models import ModMetadata
from task_builder.models.download_task import DownloadTask


class TaskBuilder(MCLBaseModel, ABC):

    @abstractmethod
    def generate_tasks(self, mods: NotEmptyList[ModMetadata]) -> List[DownloadTask]:
        pass