"""FastAPI app for Bacon distance API and static frontend.

This module defines the FastAPI application, mounts the static frontend files,
and provides endpoints:
- `/` root redirect to the static index page.
- `/api/bacon_distance` to calculate the Bacon distance of a given actor.

It also handles error mapping for actor not found and input validation errors.
"""

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
async def get_home() -> RedirectResponse:
    """Redirects the root URL to the static index page.

    This asynchronous route handler captures GET requests to the root path ("/")
    and redirects the client to the `/static/index.html` page using a 307
    Temporary Redirect.

    Returns:
        RedirectResponse: A redirect response pointing to `/static/index.html`.
    """
    return RedirectResponse(url="/static/index.html")


@app.get("/api/bacon_distance", response_model=BaconDistanceResponse)
async def handle_bacon_distance_request(
    actor_name: str = Query(...),
) -> BaconDistanceResponse:
    """Calculates the Bacon distance between the given actor and Kevin Bacon.

    This endpoint receives an actor's name as a query parameter and computes the
    Bacon distance between the specified actor and Kevin Bacon using the loaded
    movies dataset. The result is returned as a string.

    Args:
        actor_name (str): The name of the actor for whom to compute the Bacon distance.

    Returns:
        BaconDistanceResponse: A response object containing the Bacon distance as a
        string.

    Raises:
        HTTPException:
            - 400 Bad Request: If the input is invalid or a processing error occurs.
            - 404 Not Found: If the specified actor cannot be found in the dataset.
    """
    try:
        bacon_distance = calc_bacon_distance(actor_name, app.state.movies_dataset)
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
