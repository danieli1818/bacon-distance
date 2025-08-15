"""Generates a formatted movies-actors dataset from raw IMDB TSV files.

This script processes IMDB data files (`title.basics.tsv`, `title.principals.tsv`,
and `name.basics.tsv`) to create a structured dataset capturing:

- Movie titles and their associated actors.
- An actors graph showing connections weighted by shared appearances.

The resulting dataset is saved as a JSON file suitable for calculating
Bacon distances or similar analyses.

Usage:
    python generate_db.py --title_basics path/to/title.basics.tsv \
                          --title_principals path/to/title.principals.tsv \
                          --name_basics path/to/name.basics.tsv \
                          --output_file path/to/output_dataset.json
"""

import csv
import itertools
import sys
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import cast

from bacondistance.utils.consts import (
    IMDB_ACTOR_JOB_CATEGORIES,
    IMDB_MOVIE_TITLE_TYPES,
    IMDB_NAME_BASICS_ACTOR_ID_FIELD,
    IMDB_NAME_BASICS_ACTOR_NAME_FIELD,
    IMDB_TITLE_BASICS_MOVIE_ID_FIELD,
    IMDB_TITLE_BASICS_MOVIE_NAME_FIELD,
    IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD,
    IMDB_TITLE_PRINCIPALS_ACTOR_ID_FIELD,
    IMDB_TITLE_PRINCIPALS_JOB_CATEGORY_FIELD,
    IMDB_TITLE_PRINCIPALS_MOVIE_ID_FIELD,
)
from bacondistance.utils.models import MoviesActorsDataset


def load_titles_ids(
    titles_names_file_path: str | Path, titles_types: Iterable[str]
) -> dict[str, str]:
    """Loads and returns a mapping of title IDs to their names filtered by title types.

    Reads the `title.basics.tsv` file and extracts title IDs and corresponding
    names for the specified types of titles.

    Args:
        titles_names_file_path (str | Path): Path to the `title.basics.tsv` file.
        titles_types (Iterable[str]): Iterable of title types to include (e.g.,
        ['movie', 'tvSeries']).

    Returns:
        dict[str, str]: A dictionary mapping title IDs to their respective names.
    """
    titles_names_file_path = Path(titles_names_file_path)
    titles_names = {}
    with open(titles_names_file_path) as movies_names_file:
        reader = csv.DictReader(movies_names_file, delimiter="\t")
        for row in reader:
            title_type = row[IMDB_TITLE_BASICS_MOVIE_TYPE_FIELD]
            if title_type not in titles_types:
                continue
            title_id = row[IMDB_TITLE_BASICS_MOVIE_ID_FIELD]
            title_name = row[IMDB_TITLE_BASICS_MOVIE_NAME_FIELD]
            titles_names[title_id] = title_name
    return titles_names


def load_titles_workers(
    titles_workers_file_path: str | Path,
    titles_ids: Iterable[str],
    workers_types: Iterable[str],
) -> dict[str, list[str]]:
    """Loads and returns a mapping of movie IDs to lists of worker (actor) IDs.

    Parses the `title.principals.tsv` file to extract worker IDs associated
    with given title IDs, filtering by specified worker job categories.

    Args:
        titles_workers_file_path (str | Path): Path to the `title.principals.tsv` file.
        titles_ids (Iterable[str]): Iterable of title IDs to filter on.
        workers_types (Iterable[str]): Iterable of worker job categories to include
            (e.g., ['actor', 'actress']).

    Returns:
        dict[str, list[str]]: A dictionary mapping each title ID to a list of
            worker (actor) IDs involved with that title.
    """
    titles_workers_file_path = Path(titles_workers_file_path)
    titles_workers_ids = defaultdict(list)
    with open(titles_workers_file_path) as titles_workers_file:
        reader = csv.DictReader(titles_workers_file, delimiter="\t")
        for row in reader:
            title_id = row[IMDB_TITLE_PRINCIPALS_MOVIE_ID_FIELD]
            worker_job_category = row[IMDB_TITLE_PRINCIPALS_JOB_CATEGORY_FIELD]
            if title_id not in titles_ids or worker_job_category not in workers_types:
                continue
            worker_id = row[IMDB_TITLE_PRINCIPALS_ACTOR_ID_FIELD]
            titles_workers_ids[title_id].append(worker_id)
    return titles_workers_ids


def load_workers_names(
    workers_names_file_path: str | Path, workers_ids: Iterable[str]
) -> dict[str, str]:
    """Loads and returns a mapping of worker IDs to their names from the
    `name.basics.tsv` file.

    Args:
        workers_names_file_path (Union[str, Path]): Path to the `name.basics.tsv` file.
        workers_ids (Iterable[str]): Iterable of worker IDs to look up.

    Returns:
        Dict[str, str]: A dictionary mapping each worker ID to its corresponding name.
    """
    workers_names_file_path = Path(workers_names_file_path)
    workers_names = {}
    with open(workers_names_file_path) as workers_names_file:
        reader = csv.DictReader(workers_names_file, delimiter="\t")
        for row in reader:
            worker_id = row[IMDB_NAME_BASICS_ACTOR_ID_FIELD]
            if worker_id not in workers_ids:
                continue
            worker_name = row[IMDB_NAME_BASICS_ACTOR_NAME_FIELD]
            workers_names[worker_id] = worker_name
    return workers_names


def get_titles_names_to_workers_names(
    titles_ids_to_names: Mapping[str, str],
    titles_ids_to_workers_ids: Mapping[str, Iterable[str]],
    workers_ids_to_names: Mapping[str, str],
) -> dict[str, set[str]]:
    """Maps titles names to sets of their workers' names.

    Aggregates workers' names for each title name. If multiple title IDs
    share the same title name, their workers' names are combined into a set.

    Args:
        titles_ids_to_names (Mapping[str, str]): Mapping from title IDs to title names.
        titles_ids_to_workers_ids (Mapping[str, Iterable[str]]): Mapping from title
        IDs to
            iterables of worker IDs associated with the title.
        workers_ids_to_names (Mapping[str, str]): Mapping from worker IDs to worker
        names.

    Returns:
        Dict[str, Set[str]]: Dictionary mapping each title name to a set of
            associated worker names.
    """
    titles_names_to_workers_names = defaultdict(set)
    for title_id, title_name in titles_ids_to_names.items():
        if title_id not in titles_ids_to_workers_ids:
            continue
        workers_ids = titles_ids_to_workers_ids.get(title_id, [])
        workers_names = {
            workers_ids_to_names[worker_id]
            for worker_id in workers_ids
            if worker_id in workers_ids_to_names
        }
        if not workers_names:
            continue

        titles_names_to_workers_names[title_name].update(workers_names)
    return titles_names_to_workers_names


def get_actors_co_appearances_counts(
    titles_names_to_workers_names: Mapping[str, set[str]],
) -> dict[str, dict[str, int]]:
    """Computes the number of shared appearances between workers (actors).

    For each worker, returns a dictionary mapping other workers to the count
    of titles they have appeared in together.

    Args:
        titles_names_to_workers_names (Mapping[str, Set[str]]): Mapping from title
            names to sets of worker (actor) names associated with each title.

    Returns:
        Dict[str, Dict[str, int]]: A nested dictionary where the first key is a
            worker's name, and the value is another dictionary mapping coworker
            names to the count of shared appearances.
    """
    workers_to_coworkers_counts: defaultdict[str, defaultdict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    for workers_names in titles_names_to_workers_names.values():
        if len(workers_names) == 1:
            solo_actor = next(iter(workers_names))
            workers_to_coworkers_counts.setdefault(solo_actor, defaultdict(int))
        else:
            for worker1_name, worker2_name in itertools.combinations(workers_names, 2):
                workers_to_coworkers_counts[worker1_name][worker2_name] += 1
                workers_to_coworkers_counts[worker2_name][worker1_name] += 1
    return {
        worker: dict(coworkers)
        for worker, coworkers in workers_to_coworkers_counts.items()
    }


def format_dataset(
    movies_ids_to_names: Mapping[str, str],
    movies_ids_to_actors_ids: Mapping[str, Iterable[str]],
    actors_ids_to_names: Mapping[str, str],
) -> MoviesActorsDataset:
    """Formats a dataset with movie casts and an actor co-appearance graph.

    Constructs a `MoviesActorsDataset` containing:
    - `movies_casts`: a mapping from movie names to lists of actor names.
    - `actors_graph`: a mapping from actor names to other actor names,
      with the count of shared movies they have appeared in together.

    Args:
        movies_ids_to_names (Mapping[str, str]): Mapping from movie IDs to movie names.
        movies_ids_to_actors_ids (Mapping[str, Iterable[str]]): Mapping from movie IDs
            to iterables of actor IDs.
        actors_ids_to_names (Mapping[str, str]): Mapping from actor IDs to actor names.

    Returns:
        MoviesActorsDataset: The dataset including `movies_casts` and `actors_graph`.

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
    """
    movies_names_to_actors_names = get_titles_names_to_workers_names(
        movies_ids_to_names, movies_ids_to_actors_ids, actors_ids_to_names
    )
    actors_names_to_actors_movies_count = get_actors_co_appearances_counts(
        movies_names_to_actors_names
    )
    return MoviesActorsDataset(
        movies_casts=movies_names_to_actors_names,
        actors_graph=actors_names_to_actors_movies_count,
    )


def generate_db(
    title_basics_file_path: str | Path,
    title_principals_file_path: str | Path,
    name_basics_file_path: str | Path,
    output_file_path: str | Path,
):
    """Generates the movies-actors dataset from IMDB TSV files and saves it to a JSON
    file.

    Reads the IMDB files for title basics, title principals, and name basics,
    filters and formats the data into a `MoviesActorsDataset` structure, then
    serializes it as pretty-printed JSON to the specified output path.

    Args:
        title_basics_file_path (Union[str, Path]): Path to the `title.basics.tsv`
        IMDB file.
        title_principals_file_path (Union[str, Path]): Path to the
        `title.principals.tsv` IMDB file.
        name_basics_file_path (Union[str, Path]): Path to the `name.basics.tsv` IMDB
        file.
        output_file_path (Union[str, Path]): Path to save the generated dataset JSON.

    Raises:
        IOError: If any of the input files cannot be read or the output file cannot
        be written.
    """
    title_basics_file_path = Path(title_basics_file_path)
    title_principals_file_path = Path(title_principals_file_path)
    name_basics_file_path = Path(name_basics_file_path)
    output_file_path = Path(output_file_path)
    movies_ids_to_names = load_titles_ids(
        title_basics_file_path, IMDB_MOVIE_TITLE_TYPES
    )
    movies_ids_to_actors_ids = load_titles_workers(
        title_principals_file_path,
        movies_ids_to_names.keys(),
        IMDB_ACTOR_JOB_CATEGORIES,
    )
    relevant_actors_ids = set()
    for actors_ids in movies_ids_to_actors_ids.values():
        relevant_actors_ids.update(actors_ids)
    actors_ids_to_names = load_workers_names(name_basics_file_path, relevant_actors_ids)
    with open(output_file_path, "w") as output_file:
        movies_actors_dataset = format_dataset(
            movies_ids_to_names,
            cast(Mapping[str, Iterable[str]], movies_ids_to_actors_ids),
            actors_ids_to_names,
        )
        output_file.write(movies_actors_dataset.model_dump_json(indent=4))


def main(args) -> None:
    """Entry point for generating the movies-actors dataset from IMDB files.

    Calls `generate_db` with the file paths specified in `args`.

    Args:
        args: An object with the following attributes:
            - title_basics (str | Path): Path to the `title.basics.tsv` file.
            - title_principals (str | Path): Path to the `title.principals.tsv` file.
            - name_basics (str | Path): Path to the `name.basics.tsv` file.
            - output_file (str | Path): Path where the generated dataset will be saved.

    Returns:
        None
    """
    generate_db(
        args.title_basics, args.title_principals, args.name_basics, args.output_file
    )


if __name__ == "__main__":
    args_parser = ArgumentParser(
        description="Creates a formatted datasource of movies and actors from IMDB tsvs"
    )
    args_parser.add_argument(
        "--title_basics",
        "-tb",
        type=str,
        required=True,
        help="The path to the title.basics.tsv IMDB file",
    )
    args_parser.add_argument(
        "--title_principals",
        "-tp",
        type=str,
        required=True,
        help="The path to the title.principals.tsv IMDB file",
    )
    args_parser.add_argument(
        "--name_basics",
        "-nb",
        type=str,
        required=True,
        help="The path to the name.basics.tsv IMDB file",
    )
    args_parser.add_argument(
        "--output_file",
        "-o",
        type=str,
        required=True,
        help="The output json file containing the formatted dataset",
    )
    main(args_parser.parse_args(sys.argv[1:]))
