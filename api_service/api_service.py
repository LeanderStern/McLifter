from abc import ABC, abstractmethod
from typing import List

from api_service.models.get_version_response import GetVersionResponse
from base_model import MCLBaseModel


class ApiService(MCLBaseModel, ABC):

    @abstractmethod
    def get_all_project_versions(self, project_id, mod_loader) -> List[GetVersionResponse]:
        pass