import shutil
from pathlib import Path
from typing import ClassVar, List, Any

from pydantic import validate_call, PrivateAttr

from api_service.api_service import ApiService
from base_model import MCLBaseModel
from constraints import DirectoryPath
from resolver.resolver import Resolver
from task_builder.models.download_task import DownloadTask
from utils.handle_bool_input import handle_bool_input


class UpdateManager(MCLBaseModel):
    _MY_FOLDER_PATH: ClassVar[Path] = Path(__file__).parent

    resolver: Resolver
    api_service: ApiService

    _force_update: bool

    def model_post_init(self, __context: Any) -> None:
        need_force_update = self.find_force_update_candidates()
        self._force_update = handle_bool_input(
            f"Do you want to force update the following mods?\n{', '.join(need_force_update)}")

    def update_all_mods(self):
        self.backup_all_mods()
        self.execute_download_tasks(self.resolver.resolved_client_tasks)

    def backup_all_mods(self):
        client_tasks = self.resolver.resolved_client_tasks
        if len(client_tasks) > 0:
            client_folder_location: DirectoryPath = client_tasks[0].location_outdated_mod.parent
            new_client_backup_path = self._MY_FOLDER_PATH / "client_mods_backup"

            if new_client_backup_path.exists():
                shutil.rmtree(new_client_backup_path)
            shutil.copytree(client_folder_location, new_client_backup_path)

        if self.resolver.resolved_server_tasks and len(self.resolver.resolved_server_tasks) > 0:
            server_folder_location: DirectoryPath = self.resolver.resolved_server_tasks[0].location_outdated_mod.parent
            new_server_backup_path = self._MY_FOLDER_PATH / "server_mods_backup"

            if new_server_backup_path.exists():
                shutil.rmtree(new_server_backup_path)
            shutil.copytree(server_folder_location, new_server_backup_path)

    def find_force_update_candidates(self) -> List[str]:
        tasks = []

        if self.resolver.resolved_client_tasks:
            tasks.extend([task.name for task in self.resolver.resolved_client_tasks if not task.version])
        if self.resolver.resolved_server_tasks:
            tasks.extend([task.name for task in self.resolver.resolved_server_tasks if not task.version])
        return tasks

    @validate_call
    def execute_download_tasks(self, tasks: List[DownloadTask]) -> None:
        if not tasks:
            return None
        for task in tasks:
            task_version_file_data = task.version.file

            if task.version:
                task.location_outdated_mod.unlink()
                self.api_service.download_version(task.location_outdated_mod.parent, task_version_file_data.filename)
            elif self._force_update:
                self.force_update
        return None

    @validate_call
    def undo_all_changes(self):
        pass