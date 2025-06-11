import re
from typing import List

from packaging.version import Version
from packaging.specifiers import SpecifierSet, InvalidSpecifier, Specifier

from get_metadata.models import ModMetadata
from mods_dependency_checker.models.version_response import VersionResponse


class ModsDependencyChecker:

    _specifier_operators = ('~=', '==', '!=', '<=', '>=', '<', '>', '===', "*")

    def __init__(self, update_to_version: str, mods: List[ModMetadata]) -> None:
        self._mods = mods
        self.version_to_update_to = Version(update_to_version)

    @property
    def old_mods(self) -> List[ModMetadata]:
        mods = []
        for mod in self._mods:
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

    @property
    def outdated_mods(self) -> List[ModMetadata]:
        compatible_mods = [mod for mod in self._mods if mod not in self.old_mods]
        for mod in compatible_mods:
            pass


    def _does_mod_need_update(self, versions: List[str]) -> bool:
        for version in versions:
            normalized_version = self._normalize_version(version)
            if any(operator in normalized_version for operator in self._specifier_operators):
                specifier = SpecifierSet(normalized_version)
                if self.version_to_update_to not in specifier:
                    return True
            elif self.version_to_update_to > Version(normalized_version):
                return True
        return False

    @staticmethod
    def _normalize_version(version: str) -> str:
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

    @staticmethod
    def _fetch_newest_stable_version(mod: ModMetadata) -> VersionResponse:
        pass