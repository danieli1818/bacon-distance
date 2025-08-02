from typing import Dict, Set

from pydantic import BaseModel


class MoviesActorsDataset(BaseModel):
    """
    The dataset format we're going to format to.
    """
    # Movie name -> set of actors
    movies_casts: Dict[str, Set[str]]
    # Actor name -> (Co-actor name -> number of movies shared)
    actors_graph: Dict[str, Dict[str, int]]
