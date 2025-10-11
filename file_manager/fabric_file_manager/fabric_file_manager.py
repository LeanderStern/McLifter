import json
import os
import shutil
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
    _BACKUP_FOLDER_PATH: ClassVar[Path] = Path(__file__).parent / "backups"

    mod_folder_paths: NotEmptyList[DirectoryPath]
    _backup_paths: Dict[DirectoryPath, DirectoryPath] = PrivateAttr(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self._BACKUP_FOLDER_PATH.exists():
            self._BACKUP_FOLDER_PATH.mkdir()
        for path in self.mod_folder_paths:
            backup_path = self._BACKUP_FOLDER_PATH / path.parent.name
            self._backup_paths[path] = backup_path
            self.logger.info(f"backing up mods from {path} to {backup_path}\n")
            self._copy_folder(path, backup_path)

    @cached_property
    def mod_metadata(self) -> List[List[ModMetadata]] | None:
        data: List[List[ModMetadata]] = []
        for path in self.mod_folder_paths:
            data.append(self._get_all_mod_infos(path))
        return data

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

    def restore_backup(self) -> None:
        for path in self.mod_folder_paths:
            backup_path = self._backup_paths[path]
            if backup_path.exists() and any(backup_path.iterdir()):
                self._copy_folder(backup_path, path)
            else:
                raise FileNotFoundError(f"Backup folder {backup_path} doesnt contain any files.")

    @validate_call
    def _copy_folder(self, source: DirectoryPath, destination: Path) -> None:
        if not any(source.iterdir()):
            raise FileNotFoundError(f"Source folder {source} doesnt contain any files.")

        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)

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
