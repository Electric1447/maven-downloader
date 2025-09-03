from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactMetadata:
    group: str
    artifact: str
    version: str

    def to_parts(self) -> list[str]:
        return [*self.group.split('.'), self.artifact, self.version]
