from pathlib import Path
from typing import List

from pydantic import Field

from base_model import MCLBaseModel
from constraints import SemanticVersion, FilePath


class ModMetadata(MCLBaseModel):
    id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    depends: dict[str, str | List[str]]
    path: FilePath
    loader: str = Field(min_length=1)