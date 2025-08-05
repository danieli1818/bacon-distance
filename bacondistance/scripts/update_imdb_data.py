import gzip
import os
import shutil
import urllib.request
from datetime import datetime

from bacondistance.utils.paths import PROJECT_ROOT_DIR_PATH

# The URIs for the TSV files
URIS = {
    "title.basics.tsv.gz": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "name.basics.tsv.gz": "https://datasets.imdbws.com/name.basics.tsv.gz",
    "title.principals.tsv.gz": "https://datasets.imdbws.com/title.principals.tsv.gz"
}

# Directory to store the data
DATA_DIR = PROJECT_ROOT_DIR_PATH / "data"


def get_uri_last_modified_datetime(uri: str) -> datetime:
    """
    Gets the last modified time of the uri and returns it as a datetime.

    :param uri: The uri to get the last modified datetime of.
    :return: The datetime of the last modified time of the uri.
    """
    req = urllib.request.Request(uri, method='HEAD')
    with urllib.request.urlopen(req) as response:
        last_modified = response.headers.get('Last-Modified')
    return datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')


def needs_update(file_path: str, uri: str) -> bool:
    """
    Checks whether the file path needs to be updated from the given uri.
    :param file_path: The file path to check if needs an update.
    :param uri: The uri to update from if needed.
    :return: Whether the file path needs to be updated from the given uri.
    """
    if not os.path.exists(file_path):
        return True

    existing_file_timestamp = os.path.getmtime(file_path)
    existing_file_datetime = datetime.fromtimestamp(existing_file_timestamp)
    uri_file_last_modified_datetime = get_uri_last_modified_datetime(uri)

    if uri_file_last_modified_datetime > existing_file_datetime:
        return True

    return False


def download_file(file_path: str, uri: str) -> None:
    """
    Downloads the file from the uri and saves it to the file path
    """
    print(f"Downloading {uri} to {file_path}...")
    urllib.request.urlretrieve(uri, file_path)


def decompress_gz_file(gz_file_path: str, output_path: str) -> None:
    """
    Decompress a .gz file to the output path.

    :param gz_file_path: The file path to the .gz file to decompress.
    :param output_path: The file path to save the decompressed .gz file
    """
    with gzip.open(gz_file_path, 'rb') as input_file:
        with open(output_path, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)
    print(f"Decompressed {gz_file_path} to {output_path}")


def update_imdb_data() -> bool:
    """
    Updates all the IMDB tsvs file if needed.
    Returns whether a file has been updated.

    :return: Whether a file has been updated.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    has_updated = False
    for file_name, uri in URIS.items():
        file_path = os.path.join(DATA_DIR, file_name)

        if needs_update(file_path, uri):
            has_updated = True
            download_file(file_path, uri)
            decompressed_file_path, _ = os.path.splitext(file_path)
            decompress_gz_file(file_path, decompressed_file_path)
        else:
            print(f"{file_name} is already up-to-date.")
    return has_updated