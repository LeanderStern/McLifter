import copy
from functools import cached_property
from typing import List

from pydantic import validate_call

from api_service.api_service import ApiService
from api_service.enums.dependency_type_enum import DependencyTypeEnum
from api_service.models.version_response import VersionResponse
from base_model import MCLBaseModel
from download_task_builder.download_task_builder import DownloadTaskBuilder
from download_task_builder.models.download_task import DownloadTask
from exceptions import DependencyException


#Todo remove Debug prints
class ModDependencyResolver(MCLBaseModel):
    task_builder: DownloadTaskBuilder
    api_service: ApiService
    current_list_to_resolve: List[DownloadTask] | None = None

    @cached_property
    def client_download_tasks(self) -> List[DownloadTask]:
        return self.resolve_all_dependencies(self.task_builder.incompatible_client_tasks,
                                             self.task_builder.old_client_tasks)

    @cached_property
    def server_download_tasks(self) -> List[DownloadTask] | None:
        if self.task_builder.incompatible_server_tasks:
            return self.resolve_all_dependencies(self.task_builder.incompatible_server_tasks,
                                                 self.task_builder.old_server_tasks)
        else:
            return None

    @validate_call
    def resolve_all_dependencies(self, incompatible_mods: List[DownloadTask], old_mods: List[DownloadTask]) -> List[DownloadTask]:
        task_list = []
        resolved_incompatible_tasks = self._resolve_task_dependencies(incompatible_mods)
        if resolved_incompatible_tasks:
            task_list.extend(resolved_incompatible_tasks)
        else:
            raise DependencyException("Unable to resolve dependencies for incompatible client mods")

        resolved_old_tasks = self._resolve_task_dependencies(old_mods)
        if resolved_old_tasks:
            task_list.extend(resolved_old_tasks)
        elif len(old_mods) > 0:
            print("Unable to resolve dependencies for old mods")
        else:
            print("No old mods")

        return task_list

    @validate_call
    def _resolve_task_dependencies(self, list_to_resolve: List[DownloadTask]) -> List[DownloadTask] | None:
        copied_list = copy.deepcopy(list_to_resolve)
        self.current_list_to_resolve = copied_list

        for task in copied_list:
            if task.version and task.version.dependencies:
                print("resolving dependencies for", task.location_outdated_mod)
                if not self._resolve_dependencies(task.version, task):
                    return None
        self.current_list_to_resolve = None
        return copied_list

    @validate_call
    def _resolve_dependencies(self, version_to_resolve: VersionResponse, task_link: DownloadTask) -> bool:
        if self.current_list_to_resolve is None:
            raise TypeError("list_to_resolve must be set before resolving dependencies")

        for dependency in version_to_resolve.dependencies:
            #TODO remove optional
            if dependency.dependency_type is not DependencyTypeEnum.REQUIRED and dependency.dependency_type is not DependencyTypeEnum.OPTIONAL:
                continue

            if dependency.version_id:
                if dependency.version_id in self.current_list_to_resolve:
                    print(f"{dependency.version_id} already resolved")
                    continue
                version = self.api_service.get_version(dependency.version_id)
            elif dependency.project_id:
                version = self.api_service.get_project_version(dependency.project_id)
                if not version:
                    return False
            else:
                return False
            if version not in self.current_list_to_resolve and version not in task_link.dependency_versions:
                print(f"{version.id} was added to {task_link.location_outdated_mod}, now recursively resolving dependency for {version.id}")
                task_link.dependency_versions.append(version)
                self._resolve_dependencies(version, task_link)
            else:
                print(f"{version.id} already resolved")
            return True
