from pathlib import Path
from typing import List
from zipfile import ZipFile
import json

from get_mod_metadata.get_mod_metadata import GetModMetadata
from get_mod_metadata.models import ModMetadata


class FabricModsMetadata(GetModMetadata):
    _fabric_mod_info_file = "fabric.mod.json"

    @property
    def mods(self) -> List[ModMetadata]:
        if self.include_server_mods:
            return self._get_server_mods() + self._get_client_mods()
        else:
            return self._get_client_mods()

    def _get_server_mods(self) -> List[ModMetadata]:
        return self._get_all_mod_infos(self.path_to_server / "mods")

    def _get_client_mods(self) -> List[ModMetadata]:
        default_path_object = Path()
        if self.path_to_client == default_path_object:
            return self._get_all_mod_infos(default_path_object.home() / "AppData" / "Roaming" / ".minecraft" / "mods")
        else:
            return self._get_all_mod_infos(self.path_to_client)


    def _get_all_mod_infos(self, path_to_mod_folder: Path) -> List[ModMetadata]:
        if not path_to_mod_folder.is_dir():
            raise TypeError("provided path is not a folder")
        mods = []

        for path in path_to_mod_folder.iterdir():
            if path.is_file() and path.suffix == ".jar":
                with ZipFile(path, "r") as jar:
                    try:
                        with jar.open(self._fabric_mod_info_file) as json_bytes:
                            json_file: dict = json.load(json_bytes)
                    except KeyError:
                        filename_in_subfolder = f"{path.stem}/{self._fabric_mod_info_file}"
                        with jar.open(filename_in_subfolder) as json_bytes:
                            json_file: dict = json.load(json_bytes)
                mods.append(ModMetadata(id=json_file["id"], version=json_file["version"], depends=json_file["depends"], path=path))

        return mods