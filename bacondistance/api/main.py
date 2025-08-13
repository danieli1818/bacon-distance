from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from ..scripts.bacon_distance import calc_bacon_distance
from ..utils.exceptions import ActorNotFoundError
from .lifespan import lifespan
from .paths import FRONTEND_PATH
from .schemes import BaconDistanceResponse, ErrorResponse

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")


@app.get("/", response_class=RedirectResponse)
async def get_home():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/bacon_distance", response_model=BaconDistanceResponse)
async def handle_bacon_distance_request(
    actor_name: str = Query(...)) -> BaconDistanceResponse:
    try:
        bacon_distance = calc_bacon_distance(
            actor_name, app.state.movies_dataset
        )
        return BaconDistanceResponse(bacon_distance=bacon_distance)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=ErrorResponse(message=str(e)).model_dump()
        ) from e
    except ActorNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message="Actor Not Found!", description=str(e)
            ).model_dump(),
        ) from e
