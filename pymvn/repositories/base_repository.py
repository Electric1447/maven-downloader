from abc import abstractmethod

import requests
from lxml import etree
# noinspection PyProtectedMember
from lxml.etree import _Element as Element

from pymvn.models import ArtifactMetadata, POM
from pymvn.repositories.repository import Repository
from pymvn.utils.parsing_utils import parse_maven_metadata_versions, POMParser


class BaseRepository(Repository):
    def __init__(self, parser: POMParser) -> None:
        self.__parser = parser

    def list_artifact_versions(self, group_id: str, artifact_id: str) -> tuple[str, str, list[str]]:
        url = f'{self.repo_url}{group_id.replace('.', '/')}/{artifact_id}/maven-metadata.xml'
        response = requests.get(url)
        response.raise_for_status()

        xml: Element = etree.fromstring(response.content)
        return parse_maven_metadata_versions(xml)

    def get_artifact_pom(self, artifact: ArtifactMetadata) -> POM:
        url = f'{self.repo_url}{'/'.join(artifact.to_parts())}/{artifact.artifact}-{artifact.version}.pom'
        response = requests.get(url)
        response.raise_for_status()

        xml = self.__get_pom(response.text)
        return self.__parser.parse_pom(xml)

    @property
    @abstractmethod
    def repo_url(self) -> str:
        ...

    def __get_pom(self, text: str) -> Element:
        return etree.fromstring(self.__remove_namespace(text).encode('utf-8'))

    @staticmethod
    def __remove_namespace(text: str) -> str:
        project_start = text.find('<project')
        partial = text[project_start:]
        project_end = partial.find('>')
        project = partial[:project_end]

        return text.replace(project, '<project>')