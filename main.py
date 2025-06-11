import json

from utils.handle_bool_input import handle_bool_input
from utils.handle_minecraft_version_input import handle_minecraft_version_input
from get_metadata.fabric_mods_metadata.fabric_mods_metadata import FabricModsMetadata
from mods_dependency_checker.mods_dependency_checker import ModsDependencyChecker

#TODO Type Adapter for inputs and file-dependencies model config

def main() -> None:
    with open("config.json", "r") as file:
        config = json.load(file)
    update_server: bool = True #handle_bool_input("update server mods too?")

    mods_metadata = FabricModsMetadata(path_to_server=config["absolute_server_path"], include_server_mods=update_server)
    mods_metadata.mods

    update_to_version = "1.21.6" #handle_minecraft_version_input("to which version should the mods be updated?")
    dependency_checker = ModsDependencyChecker(update_to_version, mods_metadata.mods).outdated_mods
    pass


if __name__ == "__main__":
    main()