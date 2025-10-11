import json
import logging
from pathlib import Path
from typing import List

from semantic_version import Version

from api_service.modrinth_api_service.modrinth_api_service import ModrinthApiService
from constraints import DirectoryPath
from file_manager.fabric_file_manager.fabric_file_manager import FabricFileManager
from resolver.dependency_resolver.dependency_resolver import DependencyResolver
from task_builder.fabric_task_builder.fabric_task_builder import FabricTaskBuilder
from task_builder.models.download_task import DownloadTask
from update_manager.update_manager import UpdateManager
from utils.handle_bool_input import handle_bool_input
from utils.handle_minecraft_version_input import handle_minecraft_version_input


def main() -> None:
    version_to_update_to: Version = handle_minecraft_version_input("to which version should the mods be updated?")

    with open("config.json", "r") as file:
        config = json.load(file)
    server_mod_path: DirectoryPath | None = Path(config["absolute_server_mod_folder_path"]) if len(config["absolute_server_mod_folder_path"]) > 0 else None
    client_mod_path: DirectoryPath | None = None
    if len(config["absolute_client_mod_folder_path"]) <= 0:
        print("path to client mod folder not provided, using default minecraft installation path")
        client_mod_path = Path().home() / "AppData" / "Roaming" / ".minecraft" / "mods"

    paths: List[DirectoryPath] = list()
    if server_mod_path and handle_bool_input("update server mods?"):
        paths.append(server_mod_path)
    if handle_bool_input("update client mods?"):
        paths.append(client_mod_path)
    if len(paths) <= 0:
        print("bruh")
        return None

    file_manager = FabricFileManager(mod_folder_paths=paths)
    api_service = ModrinthApiService(mod_loader=file_manager.MOD_LOADER)
    task_builder = FabricTaskBuilder(api_service=api_service, version_to_update_to=version_to_update_to)
    resolver = DependencyResolver(api_service=api_service,
                                  version_to_update_to=str(version_to_update_to))

    resolved_tasks: List[DownloadTask] = list()
    for mod_folder in file_manager.mod_metadata:
        tasks = task_builder.generate_tasks(mod_folder)
        resolved_tasks.extend(resolver.resolve_dependencies(tasks))
    update_manager = UpdateManager(tasks=resolved_tasks,
                                   api_service=api_service,
                                   file_manager=file_manager,
                                   version_to_update_to=str(version_to_update_to))

    try:
        update_manager.update_all_mods()
        if handle_bool_input("undo all changes?"):
            file_manager.restore_backup()
    except Exception as E:
        file_manager.restore_backup()
        print("An error occurred during the update process. All changes have been reverted.")
        raise E

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    main()