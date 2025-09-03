import re
from typing import Any, Callable

import xmltodict

from pymvn.models import Dependency, ArtifactMetadata, DependencyScope, POM


def parse_maven_metadata_versions(metadata: dict[str, Any]) -> tuple[str, str, list[str]]:
    versioning = metadata['versioning']
    versions = versioning['versions']['version']

    latest = versioning.get('latest')
    if latest is None:
        latest = versions[-1]

    release = versioning.get('release')
    if release is None:
        release = versions[-1]

    return latest, release, versions


class POMParser:
    __PLACEHOLDER_STRING_REGEX = re.compile(r'^\${.+}$')

    def __init__(self, get_latest_version: Callable[[str, str], str]) -> None:
        self.__get_latest_version = get_latest_version

    def parse_pom(self, xml: str) -> POM:
        project: dict = xmltodict.parse(xml)['project']

        group_id = project.get('groupId')
        if group_id is None:
            group_id = project['parent']['groupId']

        artifact_id = project['artifactId']

        version = project.get('version')
        if version is None:
            version = project['parent']['version']

        dependencies = self.__parse_dependencies(self.__get_dependencies(project), version, group_id)

        return POM(
            artifact=ArtifactMetadata(
                group=group_id,
                artifact=artifact_id,
                version=version,
            ),
            dependencies=dependencies,
        )

    @staticmethod
    def __get_dependencies(project: dict[str, Any]) -> list[dict[str, str]]:
        if 'dependencies' in project:
            dependencies = project['dependencies']
        elif 'dependencyManagement' in project:
            dependencies = project['dependencyManagement']['dependencies']
        else:
            return []

        if dependencies is None:
            return []

        dependencies = dependencies['dependency']
        if isinstance(dependencies, dict):
            return [dependencies]

        return dependencies

    def __parse_dependencies(
            self,
            dependencies: list[dict[str, str]],
            project_version: str,
            project_group_id: str,
    ) -> list[Dependency]:
        return [
            self.__parse_dependency(dependency, project_version, project_group_id)
            for dependency in dependencies
            if dependency.get('optional') != 'true'
        ]

    def __parse_dependency(
            self,
            dependency: dict[str, str],
            project_version: str,
            project_group_id: str,
    ) -> Dependency:
        group_id = dependency['groupId']
        if group_id == '${project.groupId}':
            group_id = project_group_id

        artifact_id = dependency['artifactId']
        version = dependency.get('version')

        if version == '${project.version}':
            version = project_version
        elif version is None or self.__PLACEHOLDER_STRING_REGEX.match(version) is not None:
            version = self.__get_latest_version(group_id, artifact_id)

        scope = dependency.get('scope') or 'compile'

        return Dependency(
            artifact=ArtifactMetadata(
                group=group_id,
                artifact=artifact_id,
                version=version,
            ),
            scope=DependencyScope(scope),
        )
