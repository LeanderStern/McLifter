from typing import ClassVar, List, Any

from pydantic import validate_call

from api_service.api_service import ApiService
from base_model import MCLBaseModel
from constraints import SemanticVersion
from file_manager.file_manager import FileManager
from resolver.resolver import Resolver
from task_builder.models.download_task import DownloadTask
from task_builder.task_builder import TaskBuilder
from utils.handle_bool_input import handle_bool_input


class UpdateManager(MCLBaseModel):
    _BACKUP_FOLDER_CLIENT_MODS: ClassVar[str] = "client_mods_backup"
    _BACKUP_FOLDER_SERVER_MODS: ClassVar[str] = "server_mods_backup"

    resolver: Resolver
    api_service: ApiService
    file_manager: FileManager
    task_builder: TaskBuilder
    version_to_update_to: SemanticVersion

    _force_update: bool = False
    _resolved_client_tasks: List[DownloadTask] = []
    _resolved_server_tasks: List[DownloadTask] = []

    def model_post_init(self, __context: Any) -> None:
        self._resolved_client_tasks = self.resolver.resolve_dependencies(self.task_builder.incompatible_client_tasks, self.task_builder.old_client_tasks)
        if self.task_builder.incompatible_server_tasks:
            self._resolved_server_tasks = self.resolver.resolve_dependencies(self.task_builder.incompatible_server_tasks, self.task_builder.old_server_tasks)
        need_force_update = self.find_force_update_candidates()

        if need_force_update:
            self._force_update = handle_bool_input(f"Do you want to force update the following mod{'s' if len(need_force_update) > 1 else ''}?\n{', '.join(need_force_update)}")

    def update_all_mods(self):
        self.execute_download_tasks(self._resolved_client_tasks)
        if self._resolved_server_tasks:
            self.execute_download_tasks(self._resolved_server_tasks)

    def find_force_update_candidates(self) -> List[str]:
        tasks = []
        tasks.extend([task.name for task in self._resolved_client_tasks if task.needs_force_update])
        tasks.extend([task.name for task in self._resolved_server_tasks if task.needs_force_update])
        return tasks

    @validate_call
    def execute_download_tasks(self, tasks: List[DownloadTask] | None) -> None:
        if not tasks:
            return None
        for task in tasks:
            if task.version:
                task.location_outdated_mod.unlink()
                self.api_service.download_version(task.location_outdated_mod.parent,
                                                  task.version.file.url,
                                                  task.version.file.hash,
                                                  task.version.file.hash_algorithm)
                for dependency in task.dependency_versions:
                    self.api_service.download_version(task.location_outdated_mod.parent,
                                                      dependency.file.url,
                                                      dependency.file.hash,
                                                      dependency.file.hash_algorithm)
            if self._force_update and task.needs_force_update:
                self.file_manager.force_update_mod(task.location_outdated_mod.parent / task.version.file.filename, self.version_to_update_to)
        return None
