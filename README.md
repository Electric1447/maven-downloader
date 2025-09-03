# Maven Downloader (Python)

Example:

```python
from pathlib import Path

from pymvn.downloader import MavenDownloader
from pymvn.models import ArtifactMetadata

maven = MavenDownloader(Path('out'))
agp = ArtifactMetadata(
    group='com.android.tools.build',
    artifact='gradle',
    version='8.13.0',
)
artifacts = maven.get_artifact_dependencies(agp)
maven.download_artifacts(artifacts)
```