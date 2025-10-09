import json
import logging
from typing import List

from pydantic import validate_call

from api_service.api_service import ApiService
from api_service.modrinth_api_service.modrinth_api_service import ModrinthApiService
from file_manager.fabric_file_manager.fabric_file_manager import FabricFileManager
from file_manager.models import ModMetadata
from models.download_task import DownloadTask
from resolver.dependency_resolver.dependency_resolver import DependencyResolver
from update_manager.update_manager import UpdateManager
from utils.handle_bool_input import handle_bool_input
from utils.handle_minecraft_version_input import handle_minecraft_version_input


@validate_call
def build_tasks(mods: List[ModMetadata], api_service: ApiService, version_to_update_to: str) -> List[DownloadTask]:
    tasks = []
    for mod in mods:
        valid_version = api_service.get_project_version(mod.project_slug, version_to_update_to)
        if valid_version:
            tasks.append(DownloadTask(version=valid_version, location_outdated_mod=mod.path, name=mod.project_slug))
        else:
            most_recent_version = api_service.get_project_version(mod.project_slug)
            force_update_version = None if most_recent_version.version_number == mod.version else most_recent_version
            tasks.append(
                DownloadTask(version=force_update_version, location_outdated_mod=mod.path, name=mod.project_slug,
                             needs_force_update=True))
    return tasks

def main() -> None:
    update_server: bool = handle_bool_input("update server mods too?")
    version_to_update_to = handle_minecraft_version_input("to which version should the mods be updated?")

    with open("config.json", "r") as file:
        config = json.load(file)
    server_path = config["absolute_server_mod_folder_path"] if len(config["absolute_server_mod_folder_path"]) > 0 else None
    if len(config["absolute_client_mod_folder_path"]) > 0:
        file_manager = FabricFileManager(include_server_mods=update_server,
                                         path_client_mods=config["absolute_client_mod_folder_path"],
                                         path_server_mods=server_path)
    else:
        file_manager = FabricFileManager(include_server_mods=update_server,
                                         path_server_mods=server_path)

    api_service = ModrinthApiService(mod_loader=file_manager.MOD_LOADER)
    resolver = DependencyResolver(api_service=api_service,
                                  version_to_update_to=version_to_update_to)

    resolved_tasks: List[DownloadTask] = resolver.resolve_dependencies(build_tasks(file_manager.client_mods)) + resolver.resolve_dependencies(build_tasks(file_manager.server_mods))
    update_manager = UpdateManager(tasks=resolved_tasks,
                                   api_service=api_service,
                                   file_manager=file_manager,
                                   version_to_update_to=version_to_update_to)

    try:
        update_manager.update_all_mods()
        if handle_bool_input("undo all changes?"):
            file_manager.restore_backup()
    except Exception as E:
        file_manager.restore_backup()
        print("An error occurred during the update process. All changes have been reverted.")
        raise E

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()