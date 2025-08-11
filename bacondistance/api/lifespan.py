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
    """
    The lifespan function of the FastAPI app, which handles
    the loading of the app.

    :param app: The FastAPI app.
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
