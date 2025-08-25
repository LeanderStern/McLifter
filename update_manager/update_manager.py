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

    version_resolver: Resolver
    api_service: ApiService
    file_manager: FileManager
    task_builder: TaskBuilder
    version_to_update_to: SemanticVersion

    _force_update: bool = False
    _resolved_client_tasks: List[DownloadTask]
    _resolved_server_tasks: List[DownloadTask]

    def model_post_init(self, __context: Any) -> None:
        self._resolved_client_tasks = self.version_resolver.resolve_dependencies(self.task_builder.client_tasks)
        if self.task_builder.server_tasks:
            self._resolved_server_tasks = self.version_resolver.resolve_dependencies(self.task_builder.server_tasks)

        client_force_update_candidates: list[str] = self.find_force_update_candidates(self._resolved_client_tasks)
        server_force_update_candidates: list[str] = self.find_force_update_candidates(self._resolved_server_tasks) if self._resolved_server_tasks else []
        if client_force_update_candidates or server_force_update_candidates:
            multiple_force_updates: bool = len(client_force_update_candidates) + len(server_force_update_candidates) > 1
            message_parts = [f"Do you want to force update the following mod{'s' if multiple_force_updates else ''}?"]

            if client_force_update_candidates:
                message_parts.append(f"Client mods: {', '.join(client_force_update_candidates)}")
            if server_force_update_candidates:
                message_parts.append(f"Server mods: {', '.join(server_force_update_candidates)}")
            self._force_update = handle_bool_input('\n'.join(message_parts))

    def update_all_mods(self):
        self.execute_download_tasks(self._resolved_client_tasks)
        if self._resolved_server_tasks:
            self.execute_download_tasks(self._resolved_server_tasks)

    @validate_call
    def find_force_update_candidates(self, tasks: list[DownloadTask]) -> List[str]:
        return [task.name for task in tasks if task.needs_force_update]

    @validate_call
    def execute_download_tasks(self, tasks: List[DownloadTask] | None) -> None:
        if not tasks:
            return None
        for task in tasks:
            current_task_file_path = task.location_outdated_mod
            if task.version:
                current_task_file_path = task.location_outdated_mod.parent / task.version.file.filename
                task.location_outdated_mod.unlink()
                self.api_service.download_version(current_task_file_path,
                                                  task.version.file.url,
                                                  task.version.file.hash,
                                                  task.version.file.hash_algorithm)
                for dependency in task.dependency_versions:
                    self.api_service.download_version(task.location_outdated_mod.parent / dependency.file.filename,
                                                      dependency.file.url,
                                                      dependency.file.hash,
                                                      dependency.file.hash_algorithm)
            if self._force_update and task.needs_force_update:
                self.file_manager.force_update_mod(current_task_file_path, self.version_to_update_to)
        return None
