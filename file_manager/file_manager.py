import shutil
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import ClassVar, List

from pydantic import PrivateAttr

from base_model import MCLBaseModel
from constraints import SemanticVersion, FilePath, DirectoryPath
from file_manager.models import ModMetadata
from utils.copy_folder import copy_folder


class FileManager(MCLBaseModel, ABC):

    MOD_LOADER: ClassVar[str]
    _BACKUP_ROOT_FOLDER: ClassVar[Path] = Path("backup")
    _BACKUP_SOURCE_PATH_FILE_NAME: ClassVar[str] = ".source_path.txt"

    mod_folder_path: DirectoryPath

    _backup_path: DirectoryPath = PrivateAttr()

    @cached_property
    @abstractmethod
    def mod_metadata(self) -> List[ModMetadata] | None:
        """Returns a list of all the mods metadata which includes if the mod has been force updated."""

    @abstractmethod
    def force_update_mod(self, path_mod: FilePath, minecraft_version: SemanticVersion) -> None:
        """Mods that get force updated are marked inside the metadata as force updated."""

    def backup_mods(self) -> None:
        self.logger.info(f"backing up mods from {self.mod_folder_path} to {self._backup_path}\n")
        copy_folder(self.mod_folder_path, self._backup_path)

    def restore_backup(self) -> None:
        if self._backup_path.exists() and any(self._backup_path.iterdir()):
            self.copy_folder(self._backup_path, self.mod_folder_path)
        else:
            raise FileNotFoundError(f"Backup folder {self._backup_path,} doesnt contain any files.")

    @classmethod
    def get_backup_paths(cls) -> List[DirectoryPath]:
        return [file for file in cls._BACKUP_ROOT_FOLDER.iterdir() if file.is_dir()]

    @classmethod
    def get_source_path_from_backup(cls, backup_path: Path) -> DirectoryPath:
        for path in cls._BACKUP_ROOT_FOLDER.iterdir():
            if path == backup_path:
                with open(backup_path / cls._BACKUP_SOURCE_PATH_FILE_NAME) as file:
                    return Path(file.read())
        raise ValueError(f"Backup path {backup_path} not found in backup root folder.")