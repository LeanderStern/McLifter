from typing import List

from pydantic import validate_call
from semantic_version import Version

from api_service.api_service import ApiService
from constraints import NotEmptyList
from file_manager.models import ModMetadata
from task_builder.models.download_task import DownloadTask
from task_builder.task_builder import TaskBuilder


class FabricTaskBuilder(TaskBuilder):

    api_service: ApiService
    version_to_update_to: Version

    @validate_call
    def generate_tasks(self, mods: NotEmptyList[ModMetadata]) -> List[DownloadTask]:
        tasks = []
        for mod in mods:
            valid_version = self.api_service.get_project_version(mod.project_slug, str(self.version_to_update_to))
            if valid_version:
                if self.check_version_equality(mod.version, valid_version.version_number):
                    continue
                tasks.append(DownloadTask(version=valid_version, location_outdated_mod=mod.path, name=mod.project_slug))
            else:
                most_recent_version = self.api_service.get_project_version(mod.project_slug)
                if most_recent_version and not self.check_version_equality(mod.version, most_recent_version.version_number):
                    self.logger.debug(f"Newer version found for {most_recent_version.name} that needs force update")
                    force_update_version = most_recent_version
                else:
                    self.logger.debug(f"No newer version found for {mod.path.name} that needs force update")
                    force_update_version = None
                tasks.append(DownloadTask(version=force_update_version, location_outdated_mod=mod.path, name=mod.project_slug, needs_force_update=True))
        return tasks

    @validate_call
    def check_version_equality(self, version_string_a: str | None, version_string_b: str | None) -> bool:
        if version_string_a is None or version_string_b is None:
            return False
        try:
            return Version(version_string_a) == Version(version_string_b)
        except ValueError:
            return version_string_a.lower() == version_string_b.lower()