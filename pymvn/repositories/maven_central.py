import requests
from bs4 import BeautifulSoup

from pymvn.models import ArtifactMetadata
from pymvn.repositories.base_repository import BaseRepository


class MavenCentral(BaseRepository):
    def list_artifact_files(self, artifact: ArtifactMetadata) -> dict[str, str]:
        url = f'{self.repo_url}{'/'.join(artifact.to_parts())}/'
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        tags = list(soup.body.find_all('a'))[1:]
        return {name: f'{url}{name}' for name in [tag.get('href') for tag in tags]}

    @property
    def repo_url(self) -> str:
        return 'https://repo1.maven.org/maven2/'
