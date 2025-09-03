from dataclasses import dataclass

from pymvn.models.artifact_metadata import ArtifactMetadata
from pymvn.models.dependency import Dependency


@dataclass(frozen=True)
class POM:
    artifact: ArtifactMetadata
    dependencies: list[Dependency]
