from functools import cached_property
from pathlib import Path
from typing import List, ClassVar
from zipfile import ZipFile
import json

from pydantic import validate_call

from constraints import DirectoryPath
from fetch_mod_metadata.fetch_mod_metadata import FetchModMetadata
from fetch_mod_metadata.models import ModMetadata


class FetchFabricModMetadata(FetchModMetadata):
    _FABRIC_MOD_INFO_FILE: ClassVar[str] = "fabric.mod.json"

    @cached_property
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

    @validate_call
    def _get_all_mod_infos(self, path_to_mod_folder: DirectoryPath) -> List[ModMetadata]:
        mods = []
        for path in path_to_mod_folder.iterdir():
            if path.is_file() and path.suffix == ".jar":
                with ZipFile(path, "r") as jar:
                    try:
                        with jar.open(self._FABRIC_MOD_INFO_FILE) as json_bytes:
                            json_file: dict = json.load(json_bytes)
                    except KeyError:
                        filename_in_subfolder = f"{path.stem}/{self._FABRIC_MOD_INFO_FILE}"
                        with jar.open(filename_in_subfolder) as json_bytes:
                            json_file: dict = json.load(json_bytes)
                json_file["path"] = path
                json_file["loader"] = "fabric"
                mods.append(ModMetadata.model_validate(json_file))

        return mods