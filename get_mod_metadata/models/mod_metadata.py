from pathlib import Path
from typing import List

from pydantic import Field

from base_model import MCLBaseModel
from constraints import SemanticVersion


class ModMetadata(MCLBaseModel):
    id: str = Field(min_length=1)
    version: SemanticVersion
    depends: dict[str, str | List[str]]
    path: Path