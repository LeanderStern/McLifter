import shutil
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import ClassVar, List

from pydantic import PrivateAttr

from base_model import MCLBaseModel
from constraints import SemanticVersion, FilePath, DirectoryPath
from file_manager.models import ModMetadata


class FileManager(MCLBaseModel, ABC):

    MOD_LOADER: ClassVar[str]
    _BACKUP_ROOT_FOLDER: ClassVar[Path] = Path("backups")
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
        self.copy_folder(self.mod_folder_path, self._backup_path)
        with open(self._backup_path / self._BACKUP_SOURCE_PATH_FILE_NAME, "w") as file:
            file.write(str(self.mod_folder_path))

    def restore_backup(self) -> None:
        if self._backup_path.exists() and any(self._backup_path.iterdir()):
            self.copy_folder(self._backup_path, self.mod_folder_path)
        else:
            raise FileNotFoundError(f"Backup folder {self._backup_path,} doesnt contain any files.")

    @classmethod
    def get_source_paths_from_backups(cls) -> List[DirectoryPath] | None:
        if cls._BACKUP_ROOT_FOLDER.exists():
            sourced_paths = []
            for path in cls._BACKUP_ROOT_FOLDER.iterdir():
                with open(path / cls._BACKUP_SOURCE_PATH_FILE_NAME) as file:
                    sourced_paths.append(Path(file.read()))
            return sourced_paths
        return None

    @classmethod
    def copy_folder(cls, source: DirectoryPath, destination: DirectoryPath) -> None:
        if not any(source.iterdir()):
            raise FileNotFoundError(f"Source folder {source} doesnt contain any files.")

        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns(cls._BACKUP_SOURCE_PATH_FILE_NAME))