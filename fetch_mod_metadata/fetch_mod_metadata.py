from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, field_validator, Field

from base_model import MCLBaseModel
from constraints import DirectoryPath
from fetch_mod_metadata.models import ModMetadata


class FetchModMetadata(MCLBaseModel, ABC):
    path_to_server: DirectoryPath = Field(strict=False, default_factory=DirectoryPath)
    include_server_mods: bool
    path_to_client: DirectoryPath = Field(strict=False, default_factory=Path)

    @cached_property
    @abstractmethod
    def mods(self) -> List[ModMetadata]:
        pass