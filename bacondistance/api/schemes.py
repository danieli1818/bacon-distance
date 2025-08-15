"""Pydantic models for API responses.

Defines data models for:
- BaconDistanceResponse: encapsulates the Bacon distance result.
- ErrorResponse: encapsulates error details for API error responses.
"""

from pydantic import BaseModel


class BaconDistanceResponse(BaseModel):
    """Response model for the Bacon distance calculation.

    Attributes:
        bacon_distance (str): The shortest number of connections (degrees)
            between the given actor and Kevin Bacon, represented as a string.
    """

    bacon_distance: str


class ErrorResponse(BaseModel):
    """Model representing an error response.

    Attributes:
        message (str): A brief error message describing what went wrong.
        description (str | None, optional): An optional detailed description
            providing additional context about the error. Defaults to None.
    """

    message: str
    description: str | None = None
