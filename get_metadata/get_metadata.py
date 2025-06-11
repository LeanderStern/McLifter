from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, field_validator

from get_metadata.models import ModMetadata


class GetMetadata(BaseModel, ABC):
    path_to_server: str
    include_server_mods: bool
    path_to_client: Optional[str] = ""

    @field_validator("path_to_server", "path_to_client")
    @classmethod
    def validate_path(cls, string):


    @property
    @abstractmethod
    def mods(self) -> List[ModMetadata]:
        pass