from abc import abstractmethod, ABC
from functools import cached_property
from typing import List

from base_model import MCLBaseModel
from task_builder.models.download_task import DownloadTask


class Resolver(MCLBaseModel, ABC):

    @cached_property
    @abstractmethod
    def resolved_client_tasks(self) -> List[DownloadTask]:
        pass

    @cached_property
    @abstractmethod
    def resolved_server_tasks(self) -> List[DownloadTask] | None:
        pass