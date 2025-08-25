import hashlib
import json
from pathlib import Path
from typing import List, ClassVar, Any

import requests
from pydantic import validate_call, AnyHttpUrl
from requests import Response, Session
from requests.adapters import HTTPAdapter
from semantic_version import Version
from urllib3 import Retry

from api_service.api_service import ApiService
from api_service.models.version_response import VersionResponse
from api_service.modrinth_api_service.models.modrinth_version_response import ModrinthVersionResponse
from constraints import Base62Str, NotEmptyList, DirectoryPath, SemanticVersion


class ModrinthApiService(ApiService):
    mod_loader: str

    _HOST_URL: ClassVar[str] = "https://api.modrinth.com/v2"
    _GET_ALL_VERSIONS_URL: ClassVar[str] = _HOST_URL + "/project/{project_id}/version"
    _GET_VERSION_URL: ClassVar[str] = _HOST_URL + "/version/{version_id}"
    _RETRY: ClassVar[Retry] = Retry(
        total=5,
        status_forcelist=[500, 502, 503, 504]
    )
    _session: Session = requests.Session()

    def model_post_init(self, __context: Any) -> None:
        self._session.mount("https://", HTTPAdapter(max_retries=self._RETRY))

    @validate_call
    def get_project_version(self, project_slug: str, minecraft_version: SemanticVersion | None = None) -> VersionResponse | None:
        params = {"loaders": json.dumps([self.mod_loader])}
        if minecraft_version:
            params["game_versions"] = json.dumps([minecraft_version])
        response: Response = self._session.get(
            url=self._GET_ALL_VERSIONS_URL.format(project_id=project_slug),
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
        if not versions:
            return None
        return versions[0] # praying that the first version is the most stable one which it should be probably perchance maybe 👀

    @validate_call
    def get_version(self, version_id: Base62Str) -> VersionResponse:
        response = self._session.get(url=self._GET_VERSION_URL.format(version_id=version_id))
        response.raise_for_status()
        modrinth_version = ModrinthVersionResponse(**response.json())
        return VersionResponse(**modrinth_version.model_dump())

    @validate_call
    def download_version(self, path_to_new_file: Path,
                         download_link: AnyHttpUrl,
                         hash_value: str | None = None,
                         hash_algorithm: str | None = None) -> None:

        hasher = None
        response = self._session.get(download_link.unicode_string(), stream=True)

        response.raise_for_status()

        if hash_value and hash_algorithm:
            hasher = hashlib.new(hash_algorithm)

        with open(path_to_new_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                if hasher:
                    hasher.update(chunk)
        if hasher and hasher.hexdigest() != hash_value:
            raise ValueError(f"Hash mismatch for {path_to_new_file}")