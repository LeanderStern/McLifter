from functools import cached_property
from typing import List

from pydantic import validate_call
from semantic_version import Version, NpmSpec

from api_service.api_service import ApiService
from file_manager.file_manager import FileManager
from file_manager.models import ModMetadata
from task_builder.models.download_task import DownloadTask
from task_builder.task_builder import TaskBuilder


class DownloadTaskBuilder(TaskBuilder):
    file_manager: FileManager
    api_service: ApiService
    version_to_update_to: Version

    @cached_property
    def incompatible_server_tasks(self) -> List[DownloadTask] | None:
        if not self.file_manager.server_mods:
            return None
        incompatible_mods = self._get_incompatible_mods(self.file_manager.server_mods)
        return self._build_tasks(incompatible_mods)

    @cached_property
    def old_server_tasks(self) -> List[DownloadTask] | None:
        if self.incompatible_server_tasks is None:
            return None
        mods = [mod for mod in self.file_manager.server_mods if mod not in self.incompatible_server_tasks]
        return self._build_tasks(mods)


    @cached_property
    def incompatible_client_tasks(self) -> List[DownloadTask]:
        incompatible_mods = self._get_incompatible_mods(self.file_manager.client_mods)
        return self._build_tasks(incompatible_mods)

    @cached_property
    def old_client_tasks(self) -> List[DownloadTask]:
        mods = [mod for mod in self.file_manager.client_mods if mod not in self.incompatible_client_tasks]
        return self._build_tasks(mods)

    @validate_call
    def _build_tasks(self, mods: List[ModMetadata]) -> List[DownloadTask]:
        tasks = []
        for mod in mods:
            valid_version = self.api_service.get_project_version(mod.project_slug, str(self.version_to_update_to))
            if valid_version:
                tasks.append(DownloadTask(version=valid_version, location_outdated_mod=mod.path, name=mod.project_slug))
            else:
                most_recent_version = self.api_service.get_project_version(mod.project_slug)
                tasks.append(DownloadTask(version=most_recent_version, location_outdated_mod=mod.path, name=mod.project_slug, needs_force_update=True))
        return tasks

    @validate_call
    def _get_incompatible_mods(self, mods: List[ModMetadata]) -> List[ModMetadata]:
        incompatible_mods = []
        for mod in mods:
            if mod.force_updated:
                incompatible_mods.append(mod)
                continue
            if "minecraft" not in mod.depends:
                continue

            minecraft_dependency = mod.depends["minecraft"]
            if self.version_to_update_to not in NpmSpec(",".join(minecraft_dependency) if isinstance(minecraft_dependency, list) else minecraft_dependency):
                incompatible_mods.append(mod)
        return incompatible_mods