import requests

from pymvn.models import ArtifactMetadata
from pymvn.repositories.base_repository import BaseRepository


class GoogleMaven(BaseRepository):
    def list_artifact_files(self, artifact: ArtifactMetadata) -> dict[str, str]:
        base_url = f'{self.repo_url}{'/'.join(artifact.to_parts())}/'
        url = f'{base_url}artifact-metadata.json'
        response = requests.get(url)
        response.raise_for_status()

        json_data = response.json()
        return {name: f'{base_url}{name}' for name in [a['name'] for a in json_data['artifacts']]}

    @property
    def repo_url(self) -> str:
        return 'https://dl.google.com/android/maven2/'
