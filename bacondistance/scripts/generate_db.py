import sys
import csv
import itertools
from argparse import ArgumentParser
from collections import defaultdict
from typing import Dict, Iterable, List, Set

from bacondistance.utils.consts import IMDB_TITLE_BASICS_MOVIE_ID_FIELD, IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD, \
    IMDB_MOVIE_TITLE_TYPES, \
    IMDB_TITLE_BASICS_MOVIE_NAME_FIELD, IMDB_TITLE_PRINCIPALS_MOVIE_ID_FIELD, IMDB_TITLE_PRINCIPALS_ACTOR_ID_FIELD, \
    IMDB_TITLE_PRINCIPALS_JOB_CATEGORY_FIELD, IMDB_ACTOR_JOB_CATEGORIES, IMDB_NAME_BASICS_ACTOR_ID_FIELD, \
    IMDB_NAME_BASICS_ACTOR_NAME_FIELD
from bacondistance.utils.models import MoviesActorsDataset


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
    str, List[str]]:
    """
    Loads and returns the movies IDs to their list of actors IDs from the title.principals.tsv file.

    :param titles_workers_file_path: The path to the title.principals.tsv file.
    :param titles_ids: The ids of the titles.
    :param workers_types: The workers types to get.
    :return: The dict of movies IDs to their actors IDs.
    """
    titles_workers_ids = defaultdict(list)
    with open(titles_workers_file_path, 'rt') as titles_workers_file:
        reader = csv.DictReader(titles_workers_file, delimiter='\t')
        for row in reader:
            title_id = row[IMDB_TITLE_PRINCIPALS_MOVIE_ID_FIELD]
            worker_job_category = row[IMDB_TITLE_PRINCIPALS_JOB_CATEGORY_FIELD]
            if title_id not in titles_ids or worker_job_category not in workers_types:
                continue
            worker_id = row[IMDB_TITLE_PRINCIPALS_ACTOR_ID_FIELD]
            titles_workers_ids[title_id].append(worker_id)
    return titles_workers_ids


def load_workers_names(workers_names_file_path: str, workers_ids: Iterable[str]) -> Dict[str, str]:
    """
    Loads and returns the workers IDs to their names from the name.basics.tsv file.

    :param workers_names_file_path: The path to the name.basics.tsv file.
    :param workers_ids: The workers ids to load the names of.
    :return: The dict of workers IDs to their names.
    """
    workers_names = {}
    with open(workers_names_file_path, 'rt') as workers_names_file:
        reader = csv.DictReader(workers_names_file, delimiter='\t')
        for row in reader:
            worker_id = row[IMDB_NAME_BASICS_ACTOR_ID_FIELD]
            if worker_id not in workers_ids:
                continue
            worker_name = row[IMDB_NAME_BASICS_ACTOR_NAME_FIELD]
            workers_names[worker_id] = worker_name
    return workers_names


def get_titles_names_to_workers_names(titles_ids_to_names: Dict[str, str],
                                      titles_ids_to_workers_ids: Dict[str, Iterable[str]],
                                      workers_ids_to_names: Dict[str, str]) -> Dict[str, Set[str]]:
    """
    Gets the titles names to their workers names.

    :param titles_ids_to_names: dictionary from titles IDs to their names.
    :param titles_ids_to_workers_ids: dictionary from title IDs to lists of their workers IDs.
    :param workers_ids_to_names: dictionary from workers IDs to their names.
    :return: The dictionary between the titles names to their workers names (if there were multiple titles
    with the same name it combines the names of their workers)
    """
    titles_names_to_workers_names = defaultdict(set)
    for title_id, title_name in titles_ids_to_names.items():
        if title_id not in titles_ids_to_workers_ids:
            continue
        workers_ids = titles_ids_to_workers_ids.get(title_id, [])
        workers_names = {workers_ids_to_names[worker_id] for worker_id in workers_ids if
                         worker_id in workers_ids_to_names}
        if not workers_names:
            continue

        titles_names_to_workers_names[title_name].update(workers_names)
    return titles_names_to_workers_names


def get_actors_co_appearances_counts(titles_names_to_workers_names: Dict[str, Set[str]]) -> Dict[str, Dict[str, int]]:
    """
    Returns a mapping from workers names to other workers names, with the number of shared movies
    they have acted in together.

    :param titles_names_to_workers_names: The titles names to workers names dict.
    :return: The mapping from workers names to other workers names, with the number of shared movies
    they have acted in together.
    """
    workers_to_coworkers_counts = defaultdict(lambda: defaultdict(int))
    for workers_names in titles_names_to_workers_names.values():
        if len(workers_names) == 1:
            solo_actor = next(iter(workers_names))
            workers_to_coworkers_counts.setdefault(solo_actor, defaultdict(int))
        else:
            for worker1_name, worker2_name in itertools.combinations(workers_names, 2):
                workers_to_coworkers_counts[worker1_name][worker2_name] += 1
                workers_to_coworkers_counts[worker2_name][worker1_name] += 1
    return workers_to_coworkers_counts


def format_dataset(movies_ids_to_names: Dict[str, str], movies_ids_to_actors_ids: Dict[str, Iterable[str]],
                   actors_ids_to_names: Dict[str, str]) -> MoviesActorsDataset:
    """
    Formats a dataset with movie casts and an actor co-appearance graph.
    and actors graph between actors and the amount of shared movies they acted together in.

    The function takes dictionaries of movie IDs to their names, movie IDs to actor IDs,
    and actor IDs to their names. It returns a dictionary with:
    - 'movies_casts': a mapping from movie names to lists of actor names.
    - 'actors_graph': a mapping from actor names to other actor names, with the
      number of shared movies they have acted in together.

    Example:
    {
      "movies_casts": {
        "Fast & Furious": ["Vin Diesel", "Gal Gadot"],
        "Justice League": ["Gal Gadot", "Ben Affleck"],
        "Footloose": ["Kevin Bacon", "Gal Gadot", "Ben Affleck"]
      },
      "actors_graph": {
        "Vin Diesel": {"Gal Gadot": 1},
        "Gal Gadot": {"Vin Diesel": 1, "Ben Affleck": 2, "Kevin Bacon": 1},
        "Ben Affleck": {"Gal Gadot": 2, "Kevin Bacon": 1},
        "Kevin Bacon": {"Gal Gadot": 1, "Ben Affleck": 1}
      }
    }

    :param movies_ids_to_names: dictionary from movie IDs to movie names.
    :param movies_ids_to_actors_ids: dictionary from movie IDs to lists of actor IDs.
    :param actors_ids_to_names: dictionary from actor IDs to actor names.
    :return: The formatted MoviesActorsDataset dataset according to the given data.
    """

    movies_names_to_actors_names = get_titles_names_to_workers_names(movies_ids_to_names, movies_ids_to_actors_ids,
                                                                     actors_ids_to_names)
    actors_names_to_actors_movies_count = get_actors_co_appearances_counts(movies_names_to_actors_names)
    return MoviesActorsDataset(movies_casts=movies_names_to_actors_names,
                               actors_graph=actors_names_to_actors_movies_count)


def generate_db(title_basics_file_path: str, title_principals_file_path: str, name_basics_file_path: str,
                output_file_path: str):
    """
    Generates the dataset according to the given IMDB tsvs files.

    :param title_basics_file_path: The path to the title.basics.tsv IMDB file.
    :param title_principals_file_path: The path to the title.principals.tsv IMDB file.
    :param name_basics_file_path: The path to the name.basics.tsv IMDB file.
    :param output_file: The output file path to save the dataset into.
    """
    movies_ids_to_names = load_titles_ids(title_basics_file_path, IMDB_MOVIE_TITLE_TYPES)
    movies_ids_to_actors_ids = load_titles_workers(title_principals_file_path, movies_ids_to_names.keys(),
                                                   IMDB_ACTOR_JOB_CATEGORIES)
    relevant_actors_ids = set()
    for actors_ids in movies_ids_to_actors_ids.values():
        relevant_actors_ids.update(actors_ids)
    actors_ids_to_names = load_workers_names(name_basics_file_path, relevant_actors_ids)
    with open(output_file_path, 'wt') as output_file:
        movies_actors_dataset = format_dataset(movies_ids_to_names, movies_ids_to_actors_ids, actors_ids_to_names)
        output_file.write(movies_actors_dataset.model_dump_json(indent=4))


def main(args) -> None:
    generate_db(args.title_basics, args.title_principals, args.name_basics, args.output_file)


if __name__ == '__main__':
    args_parser = ArgumentParser(description='Creates a formatted datasource of movies and actors from IMDB tsvs')
    args_parser.add_argument('--title_basics', '-tb', type=str, required=True,
                             help='The path to the title.basics.tsv IMDB file')
    args_parser.add_argument('--title_principals', '-tp', type=str, required=True,
                             help='The path to the title.principals.tsv IMDB file')
    args_parser.add_argument('--name_basics', '-nb', type=str, required=True,
                             help='The path to the name.basics.tsv IMDB file')
    args_parser.add_argument('--output_file', '-o', type=str, required=True,
                             help='The output json file containing the formatted dataset')
    main(args_parser.parse_args(sys.argv[1:]))
