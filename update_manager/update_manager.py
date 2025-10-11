from typing import ClassVar, List, Any

from pydantic import validate_call

from api_service.api_service import ApiService
from base_model import MCLBaseModel
from constraints import SemanticVersion
from file_manager.file_manager import FileManager
from task_builder.models.download_task import DownloadTask
from utils.handle_bool_input import handle_bool_input


class UpdateManager(MCLBaseModel):
    _BACKUP_FOLDER_CLIENT_MODS: ClassVar[str] = "client_mods_backup"
    _BACKUP_FOLDER_SERVER_MODS: ClassVar[str] = "server_mods_backup"

    tasks: List[DownloadTask]
    api_service: ApiService
    file_manager: FileManager
    version_to_update_to: SemanticVersion

    _force_update: bool = False

    def model_post_init(self, __context: Any) -> None:
        force_update_candidates: list[DownloadTask] = self.find_force_update_candidates(self.tasks)
        number_of_candidates: int = len(force_update_candidates)
        if number_of_candidates > 0:
            message_header = (f"The following mod{'s' if number_of_candidates > 1 else ''} are not available for {self.version_to_update_to} "
                              f"do you want to force update them?")
            tasks = "\n\n".join([str(item) for item in force_update_candidates])

            self._force_update = handle_bool_input(message_header + '\n\n' + tasks)

    def update_all_mods(self) -> None:
        for task in self.tasks:
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

    @validate_call
    def find_force_update_candidates(self, tasks: list[DownloadTask]) -> List[DownloadTask]:
        candidates: List[DownloadTask] = [task for task in tasks if task.needs_force_update]

        return sorted(candidates, key=lambda task: task.location_outdated_mod)
