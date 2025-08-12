from pydantic import BaseModel


class BaconDistanceRequest(BaseModel):
    actor_name: str


class BaconDistanceResponse(BaseModel):
    bacon_distance: str


class ErrorResponse(BaseModel):
    message: str
    description: str | None = None
