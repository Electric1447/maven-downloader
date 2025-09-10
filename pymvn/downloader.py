import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Collection

from pymvn.models import ArtifactMetadata, POM, DependencyScope
from pymvn.repositories import Repositories
from pymvn.utils.artifact_utils import is_problematic_artifact, get_replacement_artifact
from pymvn.utils.download_utils import download_file


class MavenDownloader:
    def __init__(self, output_dir: Path, always_download: bool = False) -> None:
        self.__output_dir = output_dir
        self.__always_download = always_download
        self.__repositories = Repositories()

    def get_artifact_dependencies(
            self,
            artifact: ArtifactMetadata,
            excluded_scopes: Collection[DependencyScope] = None,
    ) -> set[ArtifactMetadata]:
        if excluded_scopes is None:
            excluded_scopes = []
        excluded_scopes.append(DependencyScope.Unknown)

        return self.__add_artifact_dependencies(
            pom=self.__repositories.get_artifact_pom(artifact),
            artifacts={artifact},
            excluded_scopes=excluded_scopes,
        )

    def __add_artifact_dependencies(
            self,
            pom: POM,
            artifacts: set[ArtifactMetadata],
            excluded_scopes: list[DependencyScope],
    ) -> set[ArtifactMetadata]:
        for dependency in pom.dependencies:
            artifact = dependency.artifact

            if dependency.scope in excluded_scopes:
                continue

            if is_problematic_artifact(artifact):
                artifact = get_replacement_artifact(artifact)

            if artifact is None or artifact in artifacts:
                continue

            artifacts.add(artifact)
            dependency_pom = self.__repositories.get_artifact_pom(artifact)
            self.__add_artifact_dependencies(dependency_pom, artifacts, excluded_scopes)

        return artifacts

    def download_artifacts(
            self,
            artifacts: Collection[ArtifactMetadata],
            multithreading: bool = True,
    ) -> None:
        with ThreadPoolExecutor(max_workers=os.cpu_count() if multithreading else 1) as executor:
            executor.map(self.download_artifact, artifacts)

    def download_artifact(self, artifact: ArtifactMetadata) -> None:
        print(f'Downloading: {artifact}')
        files = self.__repositories.list_artifact_files(artifact)
        artifact_dir = self.__output_dir.joinpath(*artifact.to_parts())
        if artifact_dir.exists() and not self.__always_download:
            print(f'Skipping {artifact}')
            return

        artifact_dir.mkdir(parents=True, exist_ok=True)
        for filename, url in files.items():
            download_file(url, artifact_dir / filename)
