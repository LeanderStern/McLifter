import json
import os
import shutil
from functools import cached_property
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from typing import ClassVar, List, Self, Any
from zipfile import ZipFile

from pydantic import validate_call, Field, model_validator

from constraints import DirectoryPath, FilePath, SemanticVersion
from file_manager.file_manager import FileManager
from file_manager.models import ModMetadata


class FabricFileManager(FileManager):
    MOD_LOADER: ClassVar[str] = "fabric"

    _FABRIC_MOD_INFO_FILE: ClassVar[str] = "fabric.mod.json"
    _BACKUP_FOLDER_PATH: ClassVar[Path] = Path(__file__).parent / "backups"
    _BACKUP_PATH_CLIENT_MODS: ClassVar[Path] = _BACKUP_FOLDER_PATH / "client_mods_backup"
    _BACKUP_PATH_SERVER_MODS: ClassVar[Path] = _BACKUP_FOLDER_PATH / "server_mods_backup"
    _MC_LIFTER_FORCE_UPDATED_FLAG: ClassVar[str] = "force-updated-by-MC-Lifter"

    path_server_mods: DirectoryPath | None = Field(strict=False, default=None)
    include_server_mods: bool
    path_client_mods: DirectoryPath = Field(strict=False, default=Path().home() / "AppData" / "Roaming" / ".minecraft" / "mods")

    def model_post_init(self, __context: Any) -> None:
        self.logger.debug(f"backing up mods from {self.path_client_mods} to {self._BACKUP_PATH_CLIENT_MODS}\n")
        self._copy_folder(self.path_client_mods, self._BACKUP_PATH_CLIENT_MODS)
        if self.include_server_mods and self.path_server_mods is not None:
            self.logger.debug(f"backing up server mods from {self.path_server_mods} to {self._BACKUP_PATH_SERVER_MODS}\n")
            self._copy_folder(self.path_server_mods, self._BACKUP_PATH_SERVER_MODS)

    @cached_property
    def server_mods(self) -> List[ModMetadata] | None:
        if self.include_server_mods:
            return self._get_all_mod_infos(self.path_server_mods)
        else:
            return None

    @cached_property
    def client_mods(self) -> List[ModMetadata]:
        return self._get_all_mod_infos(self.path_client_mods)

    @validate_call
    def force_update_mod(self, path_mod: FilePath, minecraft_version: SemanticVersion) -> None:
        temp_dir = Path(mkdtemp())
        metadata_path = temp_dir / self._FABRIC_MOD_INFO_FILE

        with ZipFile(path_mod, "r") as jar:
            jar.extractall(temp_dir)

        with open(metadata_path) as json_bytes:
            json_file: dict = json.load(json_bytes)
        if "custom" not in json_file:
            json_file["custom"] = {}
        json_file["custom"][self._MC_LIFTER_FORCE_UPDATED_FLAG] = True
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
        exception_string = "Backup folder {folder} is empty or does not exist."

        if self._BACKUP_PATH_CLIENT_MODS.exists() and any(self._BACKUP_PATH_CLIENT_MODS.iterdir()):
            self._copy_folder(self._BACKUP_PATH_CLIENT_MODS, self.path_client_mods)
        else:
            raise FileNotFoundError(exception_string.format(folder=self._BACKUP_PATH_CLIENT_MODS))

        if self.include_server_mods and self.path_server_mods is not None:
            if self._BACKUP_PATH_SERVER_MODS.exists() and any(self._BACKUP_PATH_SERVER_MODS.iterdir()):
                self._copy_folder(self._BACKUP_PATH_SERVER_MODS, self.path_server_mods)
            else:
                raise FileNotFoundError(exception_string.format(folder=self._BACKUP_PATH_SERVER_MODS))

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
                if "custom" in json_file and self._MC_LIFTER_FORCE_UPDATED_FLAG in json_file["custom"]:
                    metadata.force_updated = True
                mods.append(metadata)
        return mods

    @model_validator(mode="after")
    def _validate_path_to_server(self) -> Self:
        if self.path_server_mods is None and self.include_server_mods:
            raise ValueError("path_to_server must be provided if include_server_mods is True")
        return self