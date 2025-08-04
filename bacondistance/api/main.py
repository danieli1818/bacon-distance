import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .schemes import BaconDistanceResponse, BaconDistanceRequest, ErrorResponse
from ..scripts.bacon_distance import calc_bacon_distance
from ..scripts.generate_db import generate_db
from ..scripts.update_imdb_data import update_imdb_data
from ..utils.exceptions import ActorNotFoundError
from ..utils.load import load_dataset
from ..utils.paths import PROJECT_ROOT_DIR_PATH, FRONTEND_DIR_PATH

DATA_PATH = PROJECT_ROOT_DIR_PATH / "data"
DATASET_PATH = DATA_PATH / "dataset.json"

app = FastAPI()

frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FRONTEND_DIR_PATH)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Updating IMDB data...")
        if update_imdb_data():
            print("Generating dataset...")
            generate_db(DATA_PATH / "title.basics.tsv", DATA_PATH / "title.principals.tsv",
                        DATA_PATH / "name.basics.tsv", DATASET_PATH)
        print("Loading dataset...")
        app.state.movies_dataset = load_dataset(DATASET_PATH)
        print("Dataset loaded!")
    except Exception as e:
        print(f"Critical error loading dataset: {e}")
        raise RuntimeError(f"Startup failed: {e}")

    yield


@app.get("/", response_class=RedirectResponse)
async def get_home():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/bacon_distance", response_model=BaconDistanceResponse)
async def handle_bacon_distance_request(request: BaconDistanceRequest = Depends()):
    try:
        bacon_distance = calc_bacon_distance(request.actor_name, app.state.movies_dataset)
        return {"bacon_distance": bacon_distance}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=ErrorResponse(
            message=str(e)
        ).model_dump())
    except ActorNotFoundError as e:
        raise HTTPException(status_code=404, detail=ErrorResponse(
            message="Actor Not Found!",
            description=str(e)
        ).model_dump())


app.router.lifespan_context = lifespan
