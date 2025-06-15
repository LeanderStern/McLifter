import copy
from functools import cached_property
from pathlib import Path
from sys import api_version
from typing import List, ClassVar, Callable

from pydantic import validate_call, Field
from semantic_version import Version

from api_service.api_service import ApiService
from api_service.enums.dependency_type_enum import DependencyTypeEnum
from api_service.enums.version_type_enum import VersionTypeEnum
from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from constraints import NotEmptyList
from fetch_mod_metadata.models import ModMetadata
from mod_dependency_manager.models.download_task import DownloadTask
from mod_sorter.mod_sorter import ModClassifier


class ModDependencyManager(MCLBaseModel):
    mod_classifier: ModClassifier
    api_service: ApiService
    client_download_tasks: List[DownloadTask] = Field(default_factory=list)
    server_download_tasks: List[DownloadTask] | None = None
    list_to_resolve: List[DownloadTask] | None = None

    def model_post_init(self, __context) -> None:
        self.populate_downloadable_mods()

    def populate_downloadable_mods(self) -> None:
        for mod in self.mod_classifier.incompatible_client_mods:
            version = self._find_updated_version(mod.project_slug)
            self.client_download_tasks.append(DownloadTask(version=version, location_outdated_mod=mod.path))
        self._resolve_task_dependencies(self.client_download_tasks)

    def _resolve_task_dependencies(self, list_to_resolve: List[DownloadTask]) -> None:
        self.list_to_resolve = list_to_resolve

        for task in copy.deepcopy(list_to_resolve):
            if task.version and task.version.dependencies:
                print("resolving dependencies for", task.location_outdated_mod)
                task.dependency_versions.extend(self._resolve_dependencies(task.version))
        self.list_to_resolve = None

    @validate_call()
    def _resolve_dependencies(self, version: VersionResponse) -> List[VersionResponse]:
        print("resolving dependencies for", version.id)
        if self.list_to_resolve is None:
            raise TypeError("list_to_resolve must be set before resolving dependencies")

        for dependency in version.dependencies:
            if dependency.dependency_type is not DependencyTypeEnum.REQUIRED or dependency.dependency_type is not DependencyTypeEnum.OPTIONAL:
                continue
            if dependency.version_id:
                if dependency.version_id in self.client_download_tasks:
                    continue
                version = self.api_service.get_version(dependency.version_id)
            elif dependency.project_id:
                version = self._find_updated_version(dependency.project_id)
            else:
                raise Exception(f"Failed to resolve the following dependency {version.model_dump()}")
            if version not in self.list_to_resolve:
                print(version.id, "is new recursively resolving dependency")
                return [version, *self._resolve_dependencies(version)]
        return []


    def _find_updated_version(self, project_slug) -> VersionResponse | None:
        versions = self.api_service.get_all_project_versions(
            project_slug=project_slug,
            mod_loader=self.mod_classifier.mod_fetcher.MOD_LOADER,
            minecraft_version=str(self.mod_classifier.version_to_update_to)
        )
        if len(versions) > 0:
            return self.get_most_stable_version(versions)
        return None

    @validate_call
    def get_most_stable_version(self, versions: NotEmptyList[VersionResponse]) -> VersionResponse:
        sorted_versions = sorted(versions, key=self._version_sorting_key)
        return sorted_versions[0]

    @staticmethod
    def _version_sorting_key(v: VersionResponse) -> tuple[int, Version | None]:
        if v.version_number:
            return v.version_type.rank, Version(v.version_number)
        return v.version_type.rank, Version("0.0.0")
