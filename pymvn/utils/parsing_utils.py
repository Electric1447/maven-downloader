import re
from typing import Callable

# noinspection PyProtectedMember
from lxml.etree import _Element as Element

from pymvn.models import Dependency, ArtifactMetadata, DependencyScope, POM


def parse_maven_metadata_versions(xml: Element) -> tuple[str, str, list[str]]:
    versioning = get_children(next(xml.iterchildren(tag='versioning')))
    versions = [e.text for e in versioning['versions'].iterchildren()]
    latest = get_element_text(versioning, 'latest', versions[-1])
    release = get_element_text(versioning, 'release', versions[-1])

    return latest, release, versions


def get_children(element: Element) -> dict[str, Element]:
    return {e.tag: e for e in element.iterchildren() if isinstance(e, Element)}


def get_element_text(
        e: Element | dict[str, Element],
        key: str,
        default: str | None = None,
) -> str | None:
    if isinstance(e, Element):
        ret = e.find(key)
        if ret is not None:
            return ret.text

    if isinstance(e, dict):
        if key in e:
            return e[key].text

    return default


class POMParser:
    __PLACEHOLDER_STRING_REGEX = re.compile(r'^\${.+}$')

    def __init__(self, get_latest_version: Callable[[str, str], str]) -> None:
        self.__get_latest_version = get_latest_version

    def parse_pom(self, xml: Element) -> POM:
        children = get_children(xml)
        artifact_id = children['artifactId'].text

        parent_group_id = None
        parent_version = None
        if 'parent' in children:
            parent = get_children(children['parent'])
            parent_group_id = parent['groupId'].text
            parent_version = parent['version'].text

        group_id = get_element_text(children, 'groupId', parent_group_id)
        version = get_element_text(children, 'version', parent_version)

        dependencies = []
        for d in xml.iterchildren('dependencies', 'dependencyManagement'):
            if d.tag == 'dependencyManagement':
                d = d.find('dependencies')
            dependencies.extend(self.__parse_dependencies(
                d.findall('dependency'),
                version,
                group_id,
            ))

        return POM(
            artifact=ArtifactMetadata(
                group=group_id,
                artifact=artifact_id,
                version=version,
            ),
            dependencies=dependencies,
        )

    def __parse_dependencies(
            self,
            dependencies: list[Element],
            project_version: str,
            project_group_id: str,
    ) -> list[Dependency]:
        return [
            self.__parse_dependency(dependency, project_version, project_group_id)
            for dependency in dependencies
            if not self.__is_optional(dependency)
        ]

    @staticmethod
    def __is_optional(dependency: Element) -> bool:
        return get_element_text(dependency, 'optional') == 'true'

    def __parse_dependency(
            self,
            dependency: Element,
            project_version: str,
            project_group_id: str,
    ) -> Dependency:
        group_id = dependency.find('groupId').text
        if group_id == '${project.groupId}':
            group_id = project_group_id

        artifact_id = dependency.find('artifactId').text
        version = get_element_text(dependency, 'version')

        if version == '${project.version}':
            version = project_version
        elif (
                version is None
                or self.__PLACEHOLDER_STRING_REGEX.match(version) is not None
                or version.startswith('[')
        ):
            version = self.__get_latest_version(group_id, artifact_id)

        scope = get_element_text(dependency, 'scope', 'compile')

        return Dependency(
            artifact=ArtifactMetadata(
                group=group_id,
                artifact=artifact_id,
                version=version,
            ),
            scope=DependencyScope(scope),
        )
