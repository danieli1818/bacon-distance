"""Defines the MoviesActorsDataset model which represents a dataset of movies and
actors, used for Bacon distance calculations.

The model includes:
- A mapping from movie titles to sets of actor names.
- A graph representing actor co-appearances and their shared movie counts.
"""

from pydantic import BaseModel


class MoviesActorsDataset(BaseModel):
    """Represents a dataset of movies and actors for Bacon distance calculations.

    This model contains:
    - A mapping of movie names to sets of actor names (`movies_casts`).
    - A graph of actor co-appearances where each actor maps to their co-actors and the
      number of shared movies (`actors_graph`).

    Attributes:
        movies_casts (Dict[str, Set[str]]): Mapping from movie title to the set of
        actors in it.
        actors_graph (Dict[str, Dict[str, int]]): Mapping from an actor's name to a
        dictionary of co-actor names and the number of movies they appeared in together.
    """

    # Movie name -> set of actors
    movies_casts: dict[str, set[str]]
    # Actor name -> (Co-actor name -> number of movies shared)
    actors_graph: dict[str, dict[str, int]]
