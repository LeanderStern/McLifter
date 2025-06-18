import json

from semantic_version import Version

from api_service.modrinth_api_service.modrinth_api_service import ModrinthApiService
from download_task_builder.download_task_builder import DownloadTaskBuilder
from fetch_mod_metadata.fetch_fabric_mod_metadata.fetch_fabric_mod_metadata import FetchFabricModMetadata
from mod_dependency_resolver.mod_dependency_resolver import ModDependencyResolver


#TODO check for ModMetadata id references
def main() -> None:
    with open("config.json", "r") as file:
        config = json.load(file)
    update_server: bool = False#handle_bool_input("update server mods too?")
    version_to_update_to = Version("1.21.6")#handle_minecraft_version_input("to which version should the mods be updated?")

    fetcher = FetchFabricModMetadata(include_server_mods=update_server)
    api_service = ModrinthApiService(minecraft_version=str(version_to_update_to), mod_loader=fetcher.MOD_LOADER)
    builder = DownloadTaskBuilder(version_to_update_to=version_to_update_to, mod_fetcher=fetcher, api_service=api_service)

    a = ModDependencyResolver(task_builder=builder, api_service=api_service)
    a.client_download_tasks
    a.server_download_tasks
    pass

if __name__ == "__main__":
    main()