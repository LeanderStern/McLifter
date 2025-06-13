import re
from functools import cached_property
from typing import List, ClassVar

from packaging.version import Version
from packaging.specifiers import SpecifierSet, Specifier
from pydantic import validate_call

from api_service.api_service import ApiService
from base_model import MCLBaseModel
from fetch_mod_metadata.fetch_mod_metadata import FetchModMetadata
from fetch_mod_metadata.models import ModMetadata
from api_service.modrinth_api_service.models.modrinth_version_response import ModrinthVersionResponse


class ModSorter(MCLBaseModel):

    _SPECIFIER_OPERATORS: ClassVar[set[str]] = Specifier._operators.keys() #ignore

    mod_fetcher: FetchModMetadata
    version_to_update_to: Version

    @cached_property
    def incompatible_mods(self) -> List[ModMetadata]:
        mods = []
        for mod in self.mod_fetcher.mods:
            if "minecraft" not in mod.depends:
                mods.append(mod)
                continue

            if isinstance(mod.depends["minecraft"], str):
                minecraft_versions = [mod.depends["minecraft"]]
            else:
                minecraft_versions = mod.depends["minecraft"]

            if self._does_mod_need_update(minecraft_versions):
                mods.append(mod)
        return mods

    @cached_property
    def old_mods(self) -> List[ModMetadata]:
        return [mod for mod in self.mod_fetcher.mods if mod not in self.incompatible_mods]

    @validate_call
    def _does_mod_need_update(self, versions: List[str]) -> bool:
        for version in versions:
            normalized_version = self._normalize_version_string(version)
            if any(operator in normalized_version for operator in self._SPECIFIER_OPERATORS):
                specifier = SpecifierSet(normalized_version)
                if self.version_to_update_to not in specifier:
                    return True
            elif self.version_to_update_to > Version(normalized_version):
                return True
        return False

    @staticmethod
    @validate_call
    def _normalize_version_string(version: str) -> str:
        def repl(match):
            major, minor = match.groups()
            return f"~={major}.{minor}"

        replaced_wildcard_with_compatible = re.sub(
            r'(\d+)\.(\d+)\.(?:x|\*)',
            repl,
            version
        )

        removed_dashes = replaced_wildcard_with_compatible.replace("-", "")
        replaced_space_with_comma = removed_dashes.replace(" ", ",")
        replace_tilde_with_compatible = replaced_space_with_comma.replace("~", "~=")
        replace_caret_with_compatible = replace_tilde_with_compatible.replace("^", "~=")
        replace_wrong_compatible = replace_caret_with_compatible.replace("~==", "~=")

        normalized_version = replace_wrong_compatible
        return normalized_version
