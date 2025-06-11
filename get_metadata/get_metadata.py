from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, field_validator, Field

from get_metadata.models import ModMetadata


class GetMetadata(BaseModel, ABC):
    path_to_server: Path
    include_server_mods: bool
    path_to_client: Path = Field(default_factory=Path)

    @property
    @abstractmethod
    def mods(self) -> List[ModMetadata]:
        pass