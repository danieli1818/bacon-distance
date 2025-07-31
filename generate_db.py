import csv
from typing import Dict, List, Iterable

from consts import IMDB_TITLE_BASICS_MOVIE_ID_FIELD, IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD, IMDB_MOVIE_TITLE_TYPES, \
    IMDB_TITLE_BASICS_MOVIE_NAME_FIELD


def load_titles_ids(titles_names_file_path: str, titles_types: Iterable[str]) -> Dict[str, str]:
    """
    Loads and returns the titles IDs to their names from the title.basics.tsv file.

    :param titles_names_file_path: The path to the title.basics.tsv file.
    :param titles_types: The types of titles we want to get.
    :return: The dict of title IDs to their names.
    """
    titles_names = {}
    with open(titles_names_file_path, 'rt') as movies_names_file:
        reader = csv.DictReader(movies_names_file, delimiter='\t')
        for row in reader:
            title_type = row[IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD]
            if title_type not in titles_types:
                continue
            title_id = row[IMDB_TITLE_BASICS_MOVIE_ID_FIELD]
            title_name = row[IMDB_TITLE_BASICS_MOVIE_NAME_FIELD]
            titles_names[title_id] = title_name
    return titles_names


