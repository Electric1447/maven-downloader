from abc import ABC, abstractmethod

from pymvn.models import ArtifactMetadata, POM


class Repository(ABC):
    @abstractmethod
    def list_artifact_files(self, artifact: ArtifactMetadata) -> dict[str, str]:
        ...

    @abstractmethod
    def list_artifact_versions(self, group_id: str, artifact_id: str) -> tuple[str, str, list[str]]:
        ...

    @abstractmethod
    def get_artifact_pom(self, artifact: ArtifactMetadata) -> POM:
        ...
