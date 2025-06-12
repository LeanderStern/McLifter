from abc import ABC, abstractmethod
from typing import List

from api_service.models.get_version_response import GetVersionResponse
from base_model import MCLBaseModel


class ApiService(MCLBaseModel, ABC):

    @abstractmethod
    def get_version(self, version_id) -> GetVersionResponse:
        pass

    @abstractmethod
    def get_all_versions(self, project_id) -> List[GetVersionResponse]:
        pass