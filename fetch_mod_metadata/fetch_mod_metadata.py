from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import List, ClassVar, Self

from pydantic import Field, model_validator

from base_model import MCLBaseModel
from constraints import DirectoryPath
from fetch_mod_metadata.models import ModMetadata


class FetchModMetadata(MCLBaseModel, ABC):
    path_to_server: DirectoryPath | None = Field(strict=False, default=None)
    include_server_mods: bool
    path_to_client: DirectoryPath = Field(strict=False, default=Path().home() / "AppData" / "Roaming" / ".minecraft" / "mods")
    MOD_LOADER: ClassVar[str]

    @cached_property
    @abstractmethod
    def server_mods(self) -> List[ModMetadata] | None:
        pass

    @cached_property
    @abstractmethod
    def client_mods(self) -> List[ModMetadata]:
        pass

    @model_validator(mode="after")
    def validate_path_to_server(self) -> Self:
        if self.path_to_server is None and self.include_server_mods:
            raise ValueError("path_to_server must be provided if include_server_mods is True")
        return self