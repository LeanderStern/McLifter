from abc import ABC, abstractmethod
from functools import cached_property
from typing import ClassVar, List

from base_model import MCLBaseModel
from constraints import SemanticVersion, FilePath
from file_manager.models import ModMetadata


class FileManager(MCLBaseModel, ABC):
    """Will automatically back up all the directories that will be modified."""

    MOD_LOADER: ClassVar[str]

    @cached_property
    @abstractmethod
    def mod_metadata(self) -> List[List[ModMetadata]] | None:
        """Each list inside the list represents a mod folder."""

    @abstractmethod
    def force_update_mod(self, path_mod: FilePath, minecraft_version: SemanticVersion) -> None:
        """Mods that get force updated are marked inside the metadata as force updated in the custom section."""

    @abstractmethod
    def restore_backup(self) -> None:
        pass