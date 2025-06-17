import json
from typing import List, ClassVar, Any

import requests
from pydantic import validate_call, PrivateAttr
from requests import Response, Session
from requests.adapters import HTTPAdapter
from semantic_version import Version
from urllib3 import Retry
from wordsegment import segment, load

from api_service.api_service import ApiService
from api_service.models.version_response import VersionResponse
from api_service.modrinth_api_service.models.modrinth_version_response import ModrinthVersionResponse
from constraints import Base62Str, SemanticVersion, NotEmptyList


class ModrinthApiService(ApiService):
    _HOST_URL: ClassVar[str] = "https://api.modrinth.com/v2"
    _GET_ALL_VERSIONS_URL: ClassVar[str] = _HOST_URL + "/project/{project_id}/version"
    _GET_VERSION_URL: ClassVar[str] = _HOST_URL + "/version/{version_id}"
    _RETRY: ClassVar[Retry] = Retry(
        total=5,
        status_forcelist=[500, 502, 503, 504]
    )
    _session: Session = PrivateAttr(requests.Session())

    mod_loader: str
    minecraft_version: SemanticVersion

    def model_post_init(self, __context: Any) -> None:
        self._session.mount("https://", HTTPAdapter(max_retries=self._RETRY))

    @validate_call
    def get_project_version(self, project_slug: str) -> VersionResponse | None:
        params = {"loaders": json.dumps([mod_loader]), "game_versions": json.dumps([minecraft_version])}
        response: Response = self._session.get(
            url=self._GET_ALL_VERSIONS_URL.format(project_id=project_slug),
            params=params,
        )
        if response.status_code == 404:
            try:
                segments = segment(project_slug)
            except ValueError:
                load()
                segments = segment(project_slug)
            segmented_project_slug = "-".join(segments)
            response = self._session.get(
                url=self._GET_ALL_VERSIONS_URL.format(project_id=segmented_project_slug),
                params=params,
            )
        while response.status_code == 404:
            new_project_slug = input(f'Mod creator provided an invalid id "{project_slug}". Please input the correct project id or leave empty to skip this mod:')
            if len(new_project_slug) == 0:
                return None
            response = self._session.get(
                url=self._GET_ALL_VERSIONS_URL.format(project_id=new_project_slug),
                params=params,
            )
            if response.status_code == 404:
                print(f"Invalid project id: {new_project_slug}. Please try again.")

        versions: List[VersionResponse] = []
        for version in response.json():
            modrinth_version = ModrinthVersionResponse(**version)
            versions.append(VersionResponse(**modrinth_version.model_dump()))
        if versions:
            return None
        return self._select_most_stable_version(versions)

    @validate_call
    def _select_most_stable_version(self, versions: NotEmptyList[VersionResponse]) -> VersionResponse:
        sorted_versions = sorted(versions, key=self._version_sorting_key)
        return sorted_versions[0]

    @validate_call
    def get_version(self, version_id: Base62Str) -> VersionResponse:
        response = self._session.get(url=self._GET_VERSION_URL.format(version_id=version_id))
        response.raise_for_status()
        modrinth_version = ModrinthVersionResponse(**response.json())
        return VersionResponse(**modrinth_version.model_dump())

    @staticmethod
    def _version_sorting_key(v: VersionResponse) -> tuple[int, Version | None]:
        if v.version_number:
            return v.version_type.rank, Version(v.version_number)
        return v.version_type.rank, Version("0.0.0")