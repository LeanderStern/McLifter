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
    def server_tasks(self) -> List[DownloadTask] | None:
        if not self.file_manager.server_mods:
            return None
        return self._build_tasks(self.file_manager.server_mods)

    @cached_property
    def client_tasks(self) -> List[DownloadTask]:
        return self._build_tasks(self.file_manager.client_mods)

    @validate_call
    def _build_tasks(self, mods: List[ModMetadata]) -> List[DownloadTask]:
        tasks = []
        for mod in mods:
            valid_version = self.api_service.get_project_version(mod.project_slug, str(self.version_to_update_to))
            if valid_version:
                tasks.append(DownloadTask(version=valid_version, location_outdated_mod=mod.path, name=mod.project_slug))
            else:
                most_recent_version = self.api_service.get_project_version(mod.project_slug)
                force_update_version = None if most_recent_version.version_number == mod.version else most_recent_version
                tasks.append(DownloadTask(version=force_update_version, location_outdated_mod=mod.path, name=mod.project_slug, needs_force_update=True))
        return tasks