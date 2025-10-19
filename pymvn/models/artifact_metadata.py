from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactMetadata:
    group: str
    artifact: str
    version: str

    def to_parts(self) -> list[str]:
        return [*self.group.split('.'), self.artifact, self.version]

    @staticmethod
    def from_parts(parts: list[str]) -> ArtifactMetadata:
        return ArtifactMetadata(parts[0], parts[1], parts[2])

    @staticmethod
    def from_string(string: str) -> ArtifactMetadata:
        return ArtifactMetadata.from_parts(string.split(':'))
