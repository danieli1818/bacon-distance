from pydantic import BaseModel


class BaconDistanceResponse(BaseModel):
    bacon_distance: str


class ErrorResponse(BaseModel):
    message: str
    description: str | None = None
