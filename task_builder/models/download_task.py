from typing import List

from pydantic import Field

from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from constraints import FilePath
from fetch_mod_metadata.models import ModMetadata


class DownloadTask(MCLBaseModel):
    version: VersionResponse | None = None
    location_outdated_mod: FilePath
    dependency_versions: List[VersionResponse] = Field(default_factory=list)
    name: str

    def __eq__(self, other: object) -> bool:
        match other:
            case VersionResponse():
                if self.version and self.version.id == other.id:
                    return True
                else:
                    if self.dependency_versions and other in self.dependency_versions:
                        return True
                return False
            case str():
                if self.version and self.version.id == other:
                    return True
                else:
                    if self.dependency_versions and other in self.dependency_versions:
                        return True
                return False
            case ModMetadata():
                return other.path == self.location_outdated_mod
            case _:
                raise NotImplemented()