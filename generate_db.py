import csv
from typing import Dict, List

from consts import IMDB_TITLE_BASICS_MOVIE_ID_FIELD, IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD, IMDB_MOVIE_TYPES, \
    IMDB_TITLE_BASICS_MOVIE_NAME_FIELD


def load_movies_ids(movies_names_file_path: str) -> Dict[str, str]:
    """
    Loads and returns the movies IDs to their names (titles) from the title.basics.tsv file.

    :param movies_names_file_path: The path to the title.basics.tsv file.
    """
    movies_names = {}
    with open(movies_names_file_path, 'rt') as movies_names_file:
        reader = csv.DictReader(movies_names_file, delimiter='\t')
        for row in reader:
            movie_type = row[IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD]
            if movie_type not in IMDB_MOVIE_TYPES:
                continue
            movie_id = row[IMDB_TITLE_BASICS_MOVIE_ID_FIELD]
            movie_name = row[IMDB_TITLE_BASICS_MOVIE_NAME_FIELD]
            movies_names[movie_id] = movie_name
    return movies_names

