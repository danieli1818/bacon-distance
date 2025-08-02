import time
import json
from collections import deque
from typing import Dict

from models import MoviesActorsDataset


def calc_distance(actor1: str, actor2: str, movies_dataset: MoviesActorsDataset) -> int | None:
    """
    Calculates the distance between the 2 actors, if infinite returns None.
    The calculation is done by running a bidirectional BFS from the actors.

    :param actor1: The first actor name.
    :param actor2: The second actor name.
    :param movies_dataset: The dataset of movies and actors.
    :return: The bacon distance of the given actor according to the dataset,
    if infinite returns None.
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
        result = _bfs_step(actors1_queue, distances_from_actor1, distances_from_actor2, actors_graph)
        if result is not None:
            return result
        if not actors1_queue:
            break

        result = _bfs_step(actors2_queue, distances_from_actor2, distances_from_actor1, actors_graph)
        if result is not None:
            return result
    return None


def _bfs_step(queue: deque, visited_distances: Dict[str, int], other_visited_distances: Dict[str, int],
              actors_graph: Dict[str, Dict[str, int]]) -> int | None:
    """
    Runs a BFS step on the actors graph according to the current queue state and the visited nodes of
    both BFS directions.
    Returns the distance between the actors given at the start of the bidirectional BFS, if finished
    the bidirectional BFS, else None.

    :param queue: The current BFS queue of one direction (all nodes has the same distance).
    :param visited_distances: The current BFS visited nodes distances dict.
    :param other_visited_distances: The other direction BFS visited nodes distances dict.
    :param actors_graph: The actors graph from the dataset of the co-actors of each actor.
    :return: The distance between the actors given at the start of the bidirectional BFS, if finished
    the bidirectional BFS, else None.
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
