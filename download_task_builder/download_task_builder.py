from functools import cached_property
from typing import List

from pydantic import validate_call
from semantic_version import Version, NpmSpec

from api_service.api_service import ApiService
from base_model import MCLBaseModel
from download_task_builder.models.download_task import DownloadTask
from fetch_mod_metadata.fetch_mod_metadata import FetchModMetadata
from fetch_mod_metadata.models import ModMetadata


class DownloadTaskBuilder(MCLBaseModel):
    mod_fetcher: FetchModMetadata
    api_service: ApiService
    version_to_update_to: Version

    @cached_property
    def incompatible_server_tasks(self) -> List[ModMetadata] | None:
        if not self.mod_fetcher.server_mods:
            return None
        return self._get_tasks(self.mod_fetcher.server_mods)

    @cached_property
    def old_server_tasks(self) -> List[ModMetadata] | None:
        if self.incompatible_server_tasks:
            return None
        mods = [mod for mod in self.mod_fetcher.server_mods if mod not in self.incompatible_server_tasks]
        return self._get_tasks(mods)


    @cached_property
    def incompatible_client_tasks(self) -> List[ModMetadata]:
        return self._get_tasks(self.mod_fetcher.client_mods)

    @cached_property
    def old_client_tasks(self) -> List[ModMetadata]:
        mods = [mod for mod in self.mod_fetcher.client_mods if mod not in self.incompatible_client_tasks]
        return self._get_tasks(mods)

    @validate_call
    def _is_mod_incompatible(self, mod: ModMetadata) -> bool:
        if "minecraft" not in mod.depends:
            return False

        minecraft_dependency = mod.depends["minecraft"]
        if self.version_to_update_to in NpmSpec(",".join(minecraft_dependency) if isinstance(minecraft_dependency, list) else minecraft_dependency):
            return False
        return True

    @validate_call
    def _get_tasks(self, mods: List[ModMetadata]) -> List[DownloadTask]:
        tasks = []
        for mod in mods:
            if self._is_mod_incompatible(mod):
                version = self.api_service.get_project_version(mod.project_slug, self.mod_fetcher.MOD_LOADER, self.version_to_update_to)
                tasks.append(DownloadTask(version=version, location_outdated_mod=mod.path))
        return tasks
