import json
import os
import shutil
import stat
from functools import cached_property
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import ClassVar, List, Any, Dict
from zipfile import ZipFile

from pydantic import validate_call, PrivateAttr

from constraints import DirectoryPath, FilePath, SemanticVersion, NotEmptyList
from file_manager.file_manager import FileManager
from file_manager.models import ModMetadata


class FabricFileManager(FileManager):
    MOD_LOADER: ClassVar[str] = "fabric"

    _FABRIC_MOD_INFO_FILE: ClassVar[str] = "fabric.mod.json"

    mod_folder_path: DirectoryPath

    def model_post_init(self, __context: Any) -> None:
        if not self._BACKUP_ROOT_FOLDER.exists():
            self._BACKUP_ROOT_FOLDER.mkdir()
        self._backup_path = self._BACKUP_ROOT_FOLDER / self.mod_folder_path.parent.name

    @cached_property
    def mod_metadata(self) -> List[ModMetadata] | None:
        return self._get_all_mod_infos(self.mod_folder_path)

    @validate_call
    def force_update_mod(self, path_mod: FilePath, minecraft_version: SemanticVersion) -> None:
        temp_dir = Path(mkdtemp())
        metadata_path = temp_dir / self._FABRIC_MOD_INFO_FILE

        with ZipFile(path_mod, "r") as jar:
            jar.extractall(temp_dir)

        with open(metadata_path) as json_bytes:
            json_file: dict = json.load(json_bytes)
        if "minecraft" in json_file["depends"]:
            json_file["depends"]["minecraft"] = minecraft_version
        else:
            raise ValueError("The mod shouldn't be force updated if it does not depend on minecraft") #Should never happen, but just in case

        with open(metadata_path, "w", encoding="utf-8") as json_bytes:
            json.dump(json_file, json_bytes, indent=2)

        with ZipFile(path_mod, "w") as new_jar:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    new_jar.write(file_path, arcname)
        rmtree(temp_dir)

    @validate_call
    def _copy_folder(self, source: DirectoryPath, destination: Path) -> None:
        if not any(source.iterdir()):
            raise FileNotFoundError(f"Source folder {source} doesnt contain any files.")

        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        # TODO Rechte Fixen
        os.chmod(destination, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)

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
                metadata = ModMetadata(**json_file)
                mods.append(metadata)
        return mods
