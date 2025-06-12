import json

from get_mod_metadata.fabric_mods_metadata.fabric_mods_metadata import FabricModsMetadata
from mod_update_manager.mod_update_manager import ModUpdateManager
from utils.handle_minecraft_version_input import handle_semantic_version_input


#TODO Type Adapter for inputs and file-dependencies model config

def main() -> None:
    with open("config.json", "r") as file:
        config = json.load(file)
    update_server: bool = False#handle_bool_input("update server mods too?")

    mods_metadata = FabricModsMetadata(path_to_server=config["absolute_server_path"], include_server_mods=update_server)
    mods_metadata.mods

    update_to_version = handle_semantic_version_input("to which version should the mods be updated?")
    dependency_checker = ModUpdateManager(update_to_version, mods_metadata.mods).old_mods
    pass


if __name__ == "__main__":
    main()