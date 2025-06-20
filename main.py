import json

from semantic_version import Version

from api_service.modrinth_api_service.modrinth_api_service import ModrinthApiService
from fetch_mod_metadata.fetch_fabric_mod_metadata.fetch_fabric_mod_metadata import FetchFabricModMetadata
from resolver.dependency_resolver.dependency_resolver import DependencyResolver
from task_builder.download_task_builder.download_task_builder import DownloadTaskBuilder
from update_manager.update_manager import UpdateManager
from utils.handle_bool_input import handle_bool_input


#TODO check for ModMetadata id references
def main() -> None:
    with open("config.json", "r") as file:
        config = json.load(file)
    update_server: bool = True#handle_bool_input("update server mods too?")
    version_to_update_to = Version("1.21.6")#handle_minecraft_version_input("to which version should the mods be updated?")

    fetcher = FetchFabricModMetadata(include_server_mods=update_server, path_to_server=config["absolute_server_path"])
    api_service = ModrinthApiService(minecraft_version=str(version_to_update_to), mod_loader=fetcher.MOD_LOADER)
    builder = DownloadTaskBuilder(version_to_update_to=version_to_update_to, mod_fetcher=fetcher, api_service=api_service)
    resolver = DependencyResolver(task_builder=builder, api_service=api_service)
    update_manager = UpdateManager(resolver=resolver, api_service=api_service)

    update_manager.update_all_mods()
    if handle_bool_input("undo all changes?"):
        update_manager.undo_all_changes()

if __name__ == "__main__":
    main()