from dataclasses import dataclass
from enum import StrEnum, auto

from pymvn.models.artifact_metadata import ArtifactMetadata


class DependencyScope(StrEnum):
    Compile = 'compile'
    Test = 'test'
    Provided = 'provided'
    Runtime = 'runtime'
    Unknown = auto()

    @classmethod
    def _missing_(cls, value):
        return cls.Unknown


@dataclass(frozen=True)
class Dependency:
    artifact: ArtifactMetadata
    scope: DependencyScope
