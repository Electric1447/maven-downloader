from pymvn.models import ArtifactMetadata

PROBLEMATIC_ARTIFACTS: dict[ArtifactMetadata, ArtifactMetadata | None] = {
    ArtifactMetadata(
        group='regexp',
        artifact='regexp',
        version='1.3-dev',
    ): ArtifactMetadata(
        group='regexp',
        artifact='regexp',
        version='1.3'
    ),
}


def is_problematic_artifact(artifact: ArtifactMetadata) -> bool:
    return artifact in PROBLEMATIC_ARTIFACTS


def get_replacement_artifact(artifact: ArtifactMetadata) -> ArtifactMetadata | None:
    return PROBLEMATIC_ARTIFACTS[artifact]
