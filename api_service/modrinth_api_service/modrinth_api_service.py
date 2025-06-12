from typing import List

import requests
from pydantic import HttpUrl, validate_call
from pydantic.v1 import validate_arguments
from pydantic_core import from_json

from api_service.api_service import ApiService
from api_service.modrinth_api_service.models.modrinth_version_response import ModrinthVersionResponse
from constraints import Base62Str


class ModrinthApiService(ApiService):
    URL: str = "https://api.modrinth.com/v2"
    GET_VERSION_URL: str = URL + "/version/{version_id}"
    GET_ALL_VERSIONS_URL: str = URL + "/projects/{project_id}/version"

    def get_all_versions_url(self, project_id: str) -> HttpUrl:
        return HttpUrl(f"{self.URL}/projects/{project_id}/version")

    def get_all_versions(self, project_id: Base62Str) -> List[ModrinthVersionResponse]:
        pass

    @validate_call
    def get_version(self, version_id: Base62Str) -> ModrinthVersionResponse:
        response = requests.get(url=self.GET_VERSION_URL.format(version_id=version_id))
        version = ModrinthVersionResponse.model_validate(from_json(response.text))
        return version