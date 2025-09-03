from abc import abstractmethod

import requests
import xmltodict

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

        xml = xmltodict.parse(response.text)
        return parse_maven_metadata_versions(xml['metadata'])

    def get_artifact_pom(self, artifact: ArtifactMetadata) -> POM:
        url = f'{self.repo_url}{'/'.join(artifact.to_parts())}/{artifact.artifact}-{artifact.version}.pom'
        response = requests.get(url)
        response.raise_for_status()

        return self.__parser.parse_pom(response.text)

    @property
    @abstractmethod
    def repo_url(self) -> str:
        ...
