import json

from packaging.version import Version

from api_service.modrinth_api_service.modrinth_api_service import ModrinthApiService
from fetch_mod_metadata.fetch_fabric_mod_metadata.fetch_fabric_mod_metadata import FetchFabricModMetadata
from mod_update_manager.mod_update_manager import ModUpdateManager
from utils.handle_minecraft_version_input import handle_minecraft_version_input

def main() -> None:
    with open("config.json", "r") as file:
        config = json.load(file)
    update_server: bool = True#handle_bool_input("update server mods too?")

    fetcher = FetchFabricModMetadata(path_to_server=config["absolute_server_path"], include_server_mods=update_server)

    version_to_update_to = Version("1.21.6")#handle_minecraft_version_input("to which version should the mods be updated?")
    dependency_checker = ModUpdateManager(version_to_update_to=version_to_update_to,
                                          mod_fetcher=fetcher,
                                          api_service=ModrinthApiService()
    ).old_mods
    pass


if __name__ == "__main__":
    main()