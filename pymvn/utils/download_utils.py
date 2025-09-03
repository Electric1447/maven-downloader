import os

import requests


def download_file(url: str, filepath: str | os.PathLike) -> None:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as file:
            for chunk in r.iter_content(chunk_size=65536):
                file.write(chunk)
