from pydantic import Field

from base_model import MMUBaseModel
from constraints import SemanticVersion


class ModMetadata(MMUBaseModel):
    id: str = Field(min_length=1)
    version: SemanticVersion
    depends: dict[str, str]