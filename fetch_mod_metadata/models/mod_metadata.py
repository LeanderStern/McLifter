from typing import List

from pydantic import Field

from base_model import MCLBaseModel
from constraints import FilePath


class ModMetadata(MCLBaseModel):
    project_slug: str = Field(min_length=1, alias="id")
    version: str = Field(min_length=1)
    depends: dict[str, str | List[str]]
    path: FilePath
