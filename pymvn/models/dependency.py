from dataclasses import dataclass
from enum import StrEnum

from pymvn.models.artifact_metadata import ArtifactMetadata


class DependencyScope(StrEnum):
    Compile = 'compile'
    Test = 'test'
    Provided = 'provided'
    Runtime = 'runtime'


@dataclass(frozen=True)
class Dependency:
    artifact: ArtifactMetadata
    scope: DependencyScope
