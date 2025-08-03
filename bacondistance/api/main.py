import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends

from .schemes import BaconDistanceResponse, BaconDistanceRequest
from ..scripts.bacon_distance import calc_bacon_distance
from ..utils.exceptions import ActorNotFoundError
from ..utils.load import load_dataset


DATASET_PATH = os.getenv('DATASET_PATH', '/home/daniel/vscode_workspace/bacon-distance/datasources/dataset.json')

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Loading dataset...")
        app.state.movies_dataset = load_dataset(DATASET_PATH)
        print("Dataset loaded!")
    except Exception as e:
        print(f"Critical error loading dataset: {e}")
        raise RuntimeError(f"Startup failed: {e}")

    yield


@app.get("/bacon_distance", response_model=BaconDistanceResponse)
async def handle_bacon_distance_request(request: BaconDistanceRequest = Depends()):
    try:
        bacon_distance = calc_bacon_distance(request.actor_name, app.state.movies_dataset)
        return {"bacon_distance": bacon_distance}
    except (ValueError, ActorNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))


app.router.lifespan_context = lifespan
