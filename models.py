from typing import Dict, List

from pydantic import BaseModel


class MoviesActorsDataset(BaseModel):
    """
    The dataset format we're going to format to.
    """
    # Movie name -> list of actors
    movies_casts: Dict[str, List[str]]
    # Actor name -> (Co-actor name -> number of movies shared)
    actors_graph: Dict[str, Dict[str, int]]
