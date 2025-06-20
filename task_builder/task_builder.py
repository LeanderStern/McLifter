from abc import abstractmethod, ABC
from functools import cached_property
from typing import List

from base_model import MCLBaseModel
from task_builder.models.download_task import DownloadTask


class TaskBuilder(MCLBaseModel, ABC):

    @cached_property
    @abstractmethod
    def incompatible_server_tasks(self) -> List[DownloadTask] | None:
        pass

    @cached_property
    @abstractmethod
    def old_server_tasks(self) -> List[DownloadTask] | None:
        pass

    @cached_property
    @abstractmethod
    def incompatible_client_tasks(self) -> List[DownloadTask]:
        pass

    @cached_property
    @abstractmethod
    def old_client_tasks(self) -> List[DownloadTask]:
        pass