"""Calculates the Bacon distance between actors using a movies dataset.

This module provides functionality to compute the shortest connection distance
between two actors in a graph representing co-appearances in movies. It includes
a bidirectional breadth-first search implementation for efficient distance calculation.

Specifically, it supports:
- Calculating the Bacon distance between any two actors.
- A convenience function to calculate the Bacon distance to Kevin Bacon.
- A command-line interface to compute and print the Bacon distance for a given actor.

Main classes and functions:
- calc_distance: Computes shortest path distance between two actors.
- calc_bacon_distance: Computes Bacon distance from a given actor to Kevin Bacon.
- main: CLI entry point to calculate distance from command-line arguments.

Raises:
- ActorNotFoundError when an actor is not present in the dataset.

Usage:
    python calc_bacon_distance.py --actor "Tom Hanks" --dataset path/to/dataset.json
"""

import json
import os.path
import sys
from argparse import ArgumentParser
from collections import deque

from bacondistance.utils.consts import BACON_ACTOR_NAME, INFINITY_STR
from bacondistance.utils.exceptions import ActorNotFoundError
from bacondistance.utils.models import MoviesActorsDataset


def calc_distance(
    actor1: str, actor2: str, movies_dataset: MoviesActorsDataset
) -> int | None:
    """Calculates the shortest distance between two actors in the dataset.

    The distance is computed using a bidirectional breadth-first search (BFS)
    on the actors graph within the dataset. If the actors are the same, the
    distance is zero. If either actor is not found in the dataset, or if the
    distance is infinite (no connection), the function returns None.

    Args:
        actor1 (str): The name of the first actor.
        actor2 (str): The name of the second actor.
        movies_dataset (MoviesActorsDataset): The dataset containing the
            actors graph and related movie data.

    Returns:
        int | None: The shortest distance between the two actors as an integer.
            Returns None if the distance is infinite or either actor is not in
            the dataset.
    """
    if actor1 == actor2:
        return 0
    actors_graph = movies_dataset.actors_graph
    if actor1 not in actors_graph or actor2 not in actors_graph:
        # One of the actors not in the dataset, therefore infinite distance.
        return None

    actors1_queue = deque([actor1])
    actors2_queue = deque([actor2])
    distances_from_actor1 = {actor1: 0}
    distances_from_actor2 = {actor2: 0}
    while actors1_queue and actors2_queue:
        result = _bfs_step(
            actors1_queue, distances_from_actor1, distances_from_actor2, actors_graph
        )
        if result is not None:
            return result
        if not actors1_queue:
            break

        result = _bfs_step(
            actors2_queue, distances_from_actor2, distances_from_actor1, actors_graph
        )
        if result is not None:
            return result
    return None


def _bfs_step(
    queue: deque,
    visited_distances: dict[str, int],
    other_visited_distances: dict[str, int],
    actors_graph: dict[str, dict[str, int]],
) -> int | None:
    """Performs one step of bidirectional BFS on the actors graph.

    Processes all nodes at the current BFS level from one direction, updating
    distances and checking for overlap with the other BFS front. If the two
    searches meet, returns the total distance between the actors.

    Args:
        queue (deque): BFS queue for the current search direction.
        visited_distances (Dict[str, int]): Distances visited so far in this direction.
        other_visited_distances (Dict[str, int]): Distances visited in the opposite
        BFS direction.
        actors_graph (Dict[str, Dict[str, int]]): Graph mapping actors to their
        co-actors.

    Returns:
        int | None: Total distance between actors if BFS fronts meet, else None.
    """
    for _ in range(len(queue)):
        current_actor = queue.popleft()
        current_actor_distance = visited_distances[current_actor]
        new_visited_actor_distance = current_actor_distance + 1
        for co_actor in actors_graph[current_actor]:
            if co_actor in visited_distances:
                continue
            if co_actor in other_visited_distances:
                return current_actor_distance + other_visited_distances[co_actor] + 1
            visited_distances[co_actor] = new_visited_actor_distance
            queue.append(co_actor)
    return None


def calc_bacon_distance(actor_name: str, movies_dataset: MoviesActorsDataset) -> str:
    """Calculates the Bacon distance of the given actor using the dataset.

    The Bacon distance represents the number of connections between the given actor
    and Kevin Bacon. If no connection exists, a predefined infinity string is returned.

    Args:
        actor_name (str): The name of the actor to calculate the Bacon distance for.
        movies_dataset (MoviesActorsDataset): The dataset containing actors and movies.

    Returns:
        str: The Bacon distance as a string. Returns a numeric string if a path exists,
            otherwise returns a constant string representing infinity.

    Raises:
        ActorNotFoundError: If the actor is not found in the dataset.
    """
    if actor_name not in movies_dataset.actors_graph:
        raise ActorNotFoundError(actor_name)
    bacon_distance = calc_distance(actor_name, BACON_ACTOR_NAME, movies_dataset)
    if bacon_distance is not None:
        return str(bacon_distance)
    return INFINITY_STR


def main(args):
    """Calculates and prints the Bacon distance based on command-line arguments.

    This function loads the movies dataset from a JSON file specified in the
    arguments, calculates the Bacon distance for the given actor, and prints the result.

    Args:
        args: An argument namespace with the following attributes:
            - dataset (str): Path to the JSON file containing the movies dataset.
            - actor (str): The name of the actor to calculate the Bacon distance for.

    Raises:
        FileNotFoundError: If the dataset file specified in `args.dataset` does not
        exist.
    """
    if not os.path.isfile(args.dataset):
        raise FileNotFoundError(
            f"Error, datasource file: {args.datasource} wasn't found!"
        )
    with open(args.dataset) as fd:
        dataset = MoviesActorsDataset(**json.load(fd))
        actor_name = args.actor
        bacon_distance = calc_bacon_distance(actor_name, dataset)
        print(bacon_distance)


if __name__ == "__main__":
    args_parser = ArgumentParser(
        description="Calculates the bacon distance of the given actor"
    )
    args_parser.add_argument(
        "--actor",
        "-ac",
        type=str,
        required=True,
        help="The actor to calculate the bacon distance of",
    )
    args_parser.add_argument(
        "--dataset",
        "-ds",
        type=str,
        required=True,
        help="The path to the formatted dataset.json file from generate_db.py",
    )
    main(args_parser.parse_args(sys.argv[1:]))
