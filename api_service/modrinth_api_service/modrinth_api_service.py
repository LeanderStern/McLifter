import json
from typing import List, ClassVar, Any

import requests
from pydantic import validate_call, AnyHttpUrl, Field, PrivateAttr
from pydantic_core import from_json
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from api_service.api_service import ApiService
from api_service.modrinth_api_service.models.modrinth_version_response import ModrinthVersionResponse
from constraints import Base62Str, MinecraftVersion


class ModrinthApiService(ApiService):
    _GET_ALL_VERSIONS_URL: ClassVar[str] = "https://api.modrinth.com/v2/project/{project_id}/version"
    _RETRY: ClassVar[Retry] = Retry(
        total=5,
        status_forcelist=[500, 502, 503, 504]
    )
    _session: Session = PrivateAttr(requests.Session())

    def model_post_init(self, __context: Any) -> None:
        self._session.mount("https://", HTTPAdapter(max_retries=self._RETRY))

    @validate_call
    def get_all_project_versions(self, project_id: str, mod_loader: str, minecraft_version: MinecraftVersion) -> List[ModrinthVersionResponse]:
        response: Response = self._session.get(
            url=self._GET_ALL_VERSIONS_URL.format(project_id=project_id),
            params={"loaders": json.dumps([mod_loader]), "game_versions": json.dumps([minecraft_version])},
        )
        response.raise_for_status()

        versions: List[ModrinthVersionResponse] = []
        for version in response.json():
            versions.append(ModrinthVersionResponse.model_validate(version))
        return versions