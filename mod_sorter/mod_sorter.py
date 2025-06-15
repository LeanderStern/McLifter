import re
from functools import cached_property
from typing import List, ClassVar
from pydantic import validate_call
from semantic_version import Version, NpmSpec

from base_model import MCLBaseModel
from fetch_mod_metadata.fetch_mod_metadata import FetchModMetadata
from fetch_mod_metadata.models import ModMetadata


class ModClassifier(MCLBaseModel):
    mod_fetcher: FetchModMetadata
    version_to_update_to: Version

    @cached_property
    def incompatible_server_mods(self) -> List[ModMetadata] | None:
        if not self.mod_fetcher.server_mods:
            return None

        mods = []
        for mod in self.mod_fetcher.server_mods:
            if self.is_mod_incompatible(mod):
                mods.append(mod)
        return mods

    @cached_property
    def old_server_mods(self) -> List[ModMetadata] | None:
        if self.incompatible_server_mods:
            return None
        return [mod for mod in self.mod_fetcher.server_mods if mod not in self.incompatible_server_mods]

    @cached_property
    def incompatible_client_mods(self) -> List[ModMetadata]:
        mods = []
        for mod in self.mod_fetcher.client_mods:
            if self.is_mod_incompatible(mod):
                mods.append(mod)
        return mods

    @cached_property
    def old_client_mods(self) -> List[ModMetadata]:
        return [mod for mod in self.mod_fetcher.client_mods if mod not in self.incompatible_client_mods]

    def is_mod_incompatible(self, mod: ModMetadata) -> bool:
        if "minecraft" not in mod.depends:
            return False

        minecraft_dependency = mod.depends["minecraft"]
        if self.version_to_update_to in NpmSpec(",".join(minecraft_dependency) if isinstance(minecraft_dependency, list) else minecraft_dependency):
            return False
        return True