from functools import cached_property
from sys import api_version
from typing import List, ClassVar

from packaging.version import Version

from api_service.api_service import ApiService
from api_service.enums.version_type_enum import VersionTypeEnum
from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from mod_sorter.mod_sorter import ModSorter


class ModDependencyManager(MCLBaseModel):
    mod_sorter: ModSorter
    api_service: ApiService

    @cached_property
    def downloadable_mods(self) -> List[VersionResponse]:
        versions_from_incompatible_mods = []
        for mod in self.mod_sorter.incompatible_mods:
            versions = self.api_service.get_all_project_versions(
                mod.id, mod.loader,
                self.mod_sorter.version_to_update_to.base_version
            )
            if len(versions) > 0:
                stable_version = self.get_most_stable_version(versions)
                versions_from_incompatible_mods.append(stable_version)

    @staticmethod
    def get_most_stable_version(versions: List[VersionResponse]) -> VersionResponse:
        sorted_versions = sorted(versions, key=lambda v: (v.version_type.RELEASE.number, Version(v.version_number)))
        return