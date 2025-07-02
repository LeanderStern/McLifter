import json
import logging

from semantic_version import Version

from api_service.modrinth_api_service.modrinth_api_service import ModrinthApiService
from file_manager.fabric_file_manager.fabric_file_manager import FabricFileManager
from resolver.dependency_resolver.dependency_resolver import DependencyResolver
from task_builder.download_task_builder.download_task_builder import DownloadTaskBuilder
from update_manager.update_manager import UpdateManager
from utils.handle_bool_input import handle_bool_input
from utils.handle_minecraft_version_input import handle_minecraft_version_input

def main() -> None:
    with open("config.json", "r") as file:
        config = json.load(file)
    update_server: bool = handle_bool_input("update server mods too?")
    version_to_update_to = handle_minecraft_version_input("to which version should the mods be updated?")

    file_manager = FabricFileManager(include_server_mods=update_server,
                                     path_server_mods=config["absolute_server_mod_folder_path"])

    api_service = ModrinthApiService(mod_loader=file_manager.MOD_LOADER)

    builder = DownloadTaskBuilder(version_to_update_to=Version(version_to_update_to),
                                  file_manager=file_manager,
                                  api_service=api_service)

    resolver = DependencyResolver(api_service=api_service,
                                  version_to_update_to=version_to_update_to)

    update_manager = UpdateManager(resolver=resolver,
                                   api_service=api_service,
                                   file_manager=file_manager,
                                   version_to_update_to=version_to_update_to,
                                   task_builder=builder)

    try:
        update_manager.update_all_mods()
        if handle_bool_input("undo all changes?"):
            file_manager.restore_backup()
    except Exception as E:
        file_manager.restore_backup()
        print("An error occurred during the update process. All changes have been undone.")
        raise E

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()