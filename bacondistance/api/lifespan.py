"""App lifespan management for FastAPI.

This module defines the `lifespan` context manager used by the FastAPI application
to manage startup and shutdown events. It handles updating IMDB data files, generating
a local dataset from them, and loading the dataset into the application's state.

Dependencies:
    - `update_imdb_data`: Checks and updates IMDB `.tsv.gz` files if necessary.
    - `generate_db`: Processes IMDB files and creates a structured JSON dataset.
    - `load_dataset`: Loads the dataset into a Pydantic model from the generated JSON.

Raises:
    RuntimeError: If dataset loading fails during startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from bacondistance.api.paths import (
    DATASET_PATH,
    NAME_BASICS_IMDB_DATA_PATH,
    TITLE_BASICS_IMDB_DATA_PATH,
    TITLE_PRINCIPALS_IMDB_DATA_PATH,
)
from bacondistance.scripts.generate_db import generate_db
from bacondistance.scripts.update_imdb_data import update_imdb_data
from bacondistance.utils.load import load_dataset


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the application lifespan by updating and loading the IMDB dataset.

    This asynchronous context manager runs during the startup and shutdown of the
    FastAPI app.
    It attempts to update the IMDB data, generate the dataset if updates occur,
    and then load
    the dataset into the application's state.

    Args:
        app (FastAPI): The FastAPI application instance.

    Raises:
        RuntimeError: If there is a critical failure during dataset loading,
        the startup process
            is aborted with an exception.
    """
    try:
        print("Updating IMDB data...")
        if update_imdb_data():
            print("Generating dataset...")
            generate_db(
                TITLE_BASICS_IMDB_DATA_PATH,
                TITLE_PRINCIPALS_IMDB_DATA_PATH,
                NAME_BASICS_IMDB_DATA_PATH,
                DATASET_PATH,
            )
        print("Loading dataset...")
        app.state.movies_dataset = load_dataset(DATASET_PATH)
        print("Dataset loaded!")
    except Exception as e:
        print(f"Critical error loading dataset: {e}")
        raise RuntimeError(f"Startup failed: {e}") from None

    yield
