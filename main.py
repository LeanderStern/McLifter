import json

from packaging.version import Version

from api_service.modrinth_api_service.modrinth_api_service import ModrinthApiService
from fetch_mod_metadata.fetch_fabric_mod_metadata.fetch_fabric_mod_metadata import FetchFabricModMetadata
from mod_dependency_manager.mod_dependency_manager import ModDependencyManager
from mod_sorter.mod_sorter import ModSorter
from utils.handle_minecraft_version_input import handle_minecraft_version_input

def main() -> None:
    with open("config.json", "r") as file:
        config = json.load(file)
    update_server: bool = False#handle_bool_input("update server mods too?")

    fetcher = FetchFabricModMetadata(include_server_mods=update_server)

    version_to_update_to = Version("1.21.6")#handle_minecraft_version_input("to which version should the mods be updated?")
    sorter = ModSorter(version_to_update_to=version_to_update_to, mod_fetcher=fetcher)
    a = ModDependencyManager(mod_sorter=sorter, api_service=ModrinthApiService()).downloadable_mods


if __name__ == "__main__":
    main()