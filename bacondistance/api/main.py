from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from ..scripts.bacon_distance import calc_bacon_distance
from ..utils.exceptions import ActorNotFoundError
from .lifespan import lifespan
from .paths import FRONTEND_PATH
from .schemes import BaconDistanceRequest, BaconDistanceResponse, ErrorResponse

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=FRONTEND_PATH), name="static")


@app.get("/", response_class=RedirectResponse)
async def get_home():
    return RedirectResponse(url="/static/index.html")


@app.get("/api/bacon_distance", response_model=BaconDistanceResponse)
async def handle_bacon_distance_request(request: BaconDistanceRequest):
    try:
        bacon_distance = calc_bacon_distance(
            request.actor_name, app.state.movies_dataset
        )
        return {"bacon_distance": bacon_distance}
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
