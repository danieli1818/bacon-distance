"""Downloads and updates IMDB datasets by fetching the latest `.tsv.gz` files.

This module manages the retrieval and decompression of key IMDB data files:
- title.basics.tsv.gz
- name.basics.tsv.gz
- title.principals.tsv.gz

It checks the remote file's last modified HTTP header to decide whether a local
copy needs updating. If the local data is outdated or missing, it downloads the
compressed file, decompresses it, and stores it in the project data directory.

The downloading and header fetching operations are retried on failure to improve
robustness against transient network issues.

Usage:
    Call `update_imdb_data()` to perform updates for all relevant IMDB files.
"""

import gzip
import os
import shutil
import urllib.request
from datetime import datetime, timedelta

from tenacity import RetryError, retry, stop_after_attempt, wait_fixed

from bacondistance.utils.paths import PROJECT_ROOT_DIR_PATH

# The URIs for the TSV files
URIS = {
    "title.basics.tsv.gz": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "name.basics.tsv.gz": "https://datasets.imdbws.com/name.basics.tsv.gz",
    "title.principals.tsv.gz": "https://datasets.imdbws.com/title.principals.tsv.gz",
}

# Directory to store the data
DATA_DIR = PROJECT_ROOT_DIR_PATH / "data"

DEFAULT_MAX_RETRIES = 3
DEFAULT_WAIT_TIME_BETWEEN_RETRIES = 5

UPDATE_TIMEDELTA_WHEN_NO_LAST_MODIFIED_FIELD = timedelta(days=1)


@retry(
    stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
    wait=wait_fixed(DEFAULT_WAIT_TIME_BETWEEN_RETRIES),
)
def get_uri_last_modified_datetime(uri: str) -> datetime | None:
    """Retrieves the Last-Modified datetime from the HTTP headers of a given URI.

    Sends an HTTP HEAD request to the specified URI and returns the value of the
    'Last-Modified' header parsed as a `datetime` object. If the header is missing,
    returns `None`.

    This function is decorated to retry on failure up to a default maximum number
    of attempts, waiting a fixed time between retries.

    Args:
        uri (str): The URI to query.

    Returns:
        datetime | None: The parsed Last-Modified datetime if present, otherwise None.

    Raises:
        urllib.error.URLError: If the URI is unreachable or there is a network error.
        urllib.error.HTTPError: If the server responds with an error status.
    """
    req = urllib.request.Request(uri, method="HEAD")
    with urllib.request.urlopen(req) as response:
        last_modified = response.headers.get("Last-Modified")
    if last_modified:
        return datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
    return None


def needs_update(file_path: str, uri: str) -> bool:
    """Determines if a local file needs to be updated based on the remote resource's
    last modified time.

    Checks if the local file at `file_path` either does not exist or is older than the
    remote resource at `uri`. It first tries to fetch the 'Last-Modified' HTTP header
    from the URI to compare timestamps. If unavailable or on error, it falls back to
    a default timedelta threshold.

    Args:
        file_path (str): Path to the local file to check.
        uri (str): URI of the remote resource to compare against.

    Returns:
        bool: True if the file does not exist or needs updating; False otherwise.

    Raises:
        RetryError: If fetching the 'Last-Modified' header repeatedly fails (caught
        internally).
    """
    if not os.path.exists(file_path):
        return True

    existing_file_timestamp = os.path.getmtime(file_path)
    existing_file_datetime = datetime.fromtimestamp(existing_file_timestamp)

    uri_file_last_modified_datetime = None
    try:
        uri_file_last_modified_datetime = get_uri_last_modified_datetime(uri)
        if (
            uri_file_last_modified_datetime
            and uri_file_last_modified_datetime > existing_file_datetime
        ):
            # Using last modified to choose whether to update our file.
            return True
    except RetryError:
        print(f"Couldn't get last modified response on {uri}...")
    if not uri_file_last_modified_datetime:
        # No last modified field, we use our default timedelta to decide whether to
        # update.
        timediff = datetime.now() - existing_file_datetime
        return timediff >= UPDATE_TIMEDELTA_WHEN_NO_LAST_MODIFIED_FIELD
    return False


@retry(
    stop=stop_after_attempt(DEFAULT_MAX_RETRIES),
    wait=wait_fixed(DEFAULT_WAIT_TIME_BETWEEN_RETRIES),
)
def download_file(file_path: str, uri: str) -> None:
    """Downloads a file from a given URI and saves it to the specified file path.

    This function attempts to download the file, retrying on failure up to a default
    maximum number of attempts with fixed wait intervals between retries.

    Args:
        file_path (str): The local path where the downloaded file will be saved.
        uri (str): The URI of the file to download.

    Raises:
        urllib.error.URLError: If the download fails due to network issues.
        urllib.error.HTTPError: If the HTTP request returns an error status.
        RetryError: If all retry attempts fail.
    """
    print(f"Downloading {uri} to {file_path}...")
    urllib.request.urlretrieve(uri, file_path)
    print(f"File downloaded successfully to {file_path}!")


def decompress_gz_file(gz_file_path: str, output_path: str) -> None:
    """Decompresses a .gz file and writes the output to a specified file path.

    Opens the `.gz` file at `gz_file_path`, decompresses its contents, and writes
    the result to `output_path`.

    Args:
        gz_file_path (str): Path to the `.gz` compressed file.
        output_path (str): Path where the decompressed content will be written.

    Raises:
        OSError: If the input or output files cannot be opened or written to.
        gzip.BadGzipFile: If the input file is not a valid `.gz` file.
    """
    with gzip.open(gz_file_path, "rb") as input_file:
        with open(output_path, "wb") as output_file:
            shutil.copyfileobj(input_file, output_file)
    print(f"Decompressed {gz_file_path} to {output_path}")


def update_imdb_data() -> bool:
    """Updates all necessary IMDB `.tsv.gz` files if newer versions are available.

    For each file in `URIS`, checks whether the local copy is outdated compared to
    the remote version (using the Last-Modified header or a fallback time threshold).
    If an update is needed, the file is downloaded and decompressed into the
    `DATA_DIR` directory.

    Returns:
        bool: True if any file was updated; False otherwise.

    Raises:
        RetryError: If a file needs to be downloaded and all download retries fail.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    has_updated = False
    for file_name, uri in URIS.items():
        file_path = os.path.join(DATA_DIR, file_name)

        if needs_update(file_path, uri):
            try:
                download_file(file_path, uri)
                decompressed_file_path, _ = os.path.splitext(file_path)
                decompress_gz_file(file_path, decompressed_file_path)
                has_updated = True
            except RetryError as e:
                print(f"Couldn't download file from {uri}...")
                if os.path.exists(file_path):
                    print(f"Using existing version of {file_name}")
                else:
                    raise e
        else:
            print(f"{file_name} is already up-to-date.")
    return has_updated
