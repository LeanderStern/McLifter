import copy
from typing import List

from pydantic import validate_call, PrivateAttr

from api_service.api_service import ApiService
from api_service.enums.dependency_type_enum import DependencyTypeEnum
from api_service.models.version_response import VersionResponse
from constraints import SemanticVersion
from models.download_task import DownloadTask
from resolver.exceptions import DependencyException
from resolver.resolver import Resolver


class DependencyResolver(Resolver):
    api_service: ApiService
    version_to_update_to: SemanticVersion

    _all_current_tasks_to_resolve: List[DownloadTask] | None = PrivateAttr(None)

    @validate_call
    def resolve_dependencies(self, tasks: List[DownloadTask]) -> List[DownloadTask]:
        # There could be a case where a task has a version that needs a force update and has a dependencies that needs a different version of the same mod
        # if that ever happens, and it causes issues, change the logic in the resolver to ignore the dependencies of a task when it has the needs_force_update flag
        task_list = []
        resolved_tasks = self._resolve_task_dependencies(tasks)
        if resolved_tasks:
            task_list.extend(resolved_tasks)
        elif resolved_tasks is None:
            raise DependencyException("Unable to resolve dependencies")

        return task_list

    @validate_call
    def _resolve_task_dependencies(self, list_to_resolve: List[DownloadTask]) -> List[DownloadTask] | None:
        if len(list_to_resolve) < 1:
            return []
        copied_list = copy.deepcopy(list_to_resolve)
        self._all_current_tasks_to_resolve = copied_list

        for task in copied_list:
            if task.version and task.version.dependencies:
                self.logger.debug(f"resolving dependencies for {task.name}")
                if not self._resolve_version(task.version, task):
                    return None
        self._all_current_tasks_to_resolve = None
        return copied_list

    @validate_call
    def _resolve_version(self, version_to_resolve: VersionResponse, task_link: DownloadTask) -> bool:
        if self._all_current_tasks_to_resolve is None:
            raise TypeError("list_to_resolve must be set before resolving dependencies")

        for dependency in version_to_resolve.dependencies:
            if dependency.dependency_type is not DependencyTypeEnum.REQUIRED:
                continue

            if dependency.version_id:
                if dependency.version_id in self._all_current_tasks_to_resolve:
                    self.logger.debug(f"{dependency.file_name} already resolved")
                    continue
                version = self.api_service.get_version(dependency.version_id)
            elif dependency.project_id:
                version = self.api_service.get_project_version(dependency.project_id, self.version_to_update_to)
                if not version:
                    self.logger.warning(f"There is no compatible version of {dependency.file_name or dependency.project_id}"
                                        f"for {self.version_to_update_to} which is required for {version_to_resolve.name}")
                    return False
            else:
                self.logger.warning(f"{dependency} has neither version_id nor project_id, cannot resolve")
                return False
            if version not in self._all_current_tasks_to_resolve and version not in task_link.dependency_versions:
                self.logger.debug(f"{version.name} was added to {task_link.location_outdated_mod}, now recursively resolving dependency for {version.name}")
                task_link.dependency_versions.append(version)
                self._resolve_version(version, task_link)
            else:
                self.logger.debug(f"{version.name} already resolved")
        return True