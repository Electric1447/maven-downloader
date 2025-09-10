from typing import Any, Callable

import requests

from pymvn.models import ArtifactMetadata, POM
from pymvn.repositories.exceptions import ArtifactNotFound
from pymvn.repositories.google_maven import GoogleMaven
from pymvn.repositories.maven_central import MavenCentral
from pymvn.repositories.repository import Repository
from pymvn.utils.parsing_utils import POMParser


class Repositories(Repository):
    def __init__(self) -> None:
        parser = POMParser(self.__get_latest_version)
        self.__repositories = [MavenCentral(parser), GoogleMaven(parser)]

    def list_artifact_files(self, artifact: ArtifactMetadata) -> dict[str, str]:
        return self.__foreach_repository(lambda repo: repo.list_artifact_files(artifact))

    def list_artifact_versions(self, group_id: str, artifact_id: str) -> tuple[str, str, list[str]]:
        return self.__foreach_repository(lambda repo: repo.list_artifact_versions(group_id, artifact_id))

    def get_artifact_pom(self, artifact: ArtifactMetadata) -> POM:
        print(f'get_artifact_pom: {artifact}')
        return self.__foreach_repository(lambda repo: repo.get_artifact_pom(artifact))

    def __foreach_repository(self, method: Callable[[Repository], Any]) -> Any:
        for repository in self.__repositories:
            try:
                return method(repository)
            except requests.HTTPError:
                continue

        raise ArtifactNotFound('Artifact was not found in any of the repositories')

    def __get_latest_version(self, group_id, artifact_id) -> str:
        return self.list_artifact_versions(group_id, artifact_id)[0]
