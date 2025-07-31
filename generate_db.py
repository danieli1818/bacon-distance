import csv
from collections import defaultdict
from typing import Dict, List, Iterable, Set

from consts import IMDB_TITLE_BASICS_MOVIE_ID_FIELD, IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD, IMDB_MOVIE_TITLE_TYPES, \
    IMDB_TITLE_BASICS_MOVIE_NAME_FIELD, IMDB_TITLE_PRINCIPALS_MOVIE_ID_FIELD, IMDB_TITLE_PRINCIPALS_ACTOR_ID_FIELD, \
    IMDB_TITLE_PRINCIPALS_JOB_CATEGORY_FIELD, IMDB_ACTOR_JOB_CATEGORIES


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


def load_titles_workers(titles_workers_file_path: str, titles_ids: Iterable[str], workers_types: Iterable[str]) -> Dict[
    str, Set[str]]:
    """
    Loads and returns the movies IDs to their list of actors IDs from the title.principals.tsv file.

    :param titles_workers_file_path: The path to the title.principals.tsv file.
    :param titles_ids: The ids of the titles.
    :param workers_types: The workers types to get.
    :return: The dict of movies IDs to their actors IDs.
    """
    titles_workers_ids = defaultdict(set)
    with open(titles_workers_file_path, 'rt') as titles_workers_file:
        reader = csv.DictReader(titles_workers_file, delimiter='\t')
        for row in reader:
            title_id = row[IMDB_TITLE_PRINCIPALS_MOVIE_ID_FIELD]
            worker_job_category = row[IMDB_TITLE_PRINCIPALS_JOB_CATEGORY_FIELD]
            if title_id not in titles_ids or worker_job_category not in workers_types:
                continue
            worker_id = row[IMDB_TITLE_PRINCIPALS_ACTOR_ID_FIELD]
            titles_workers_ids[title_id].add(worker_id)
    return titles_workers_ids

