"""This module defines custom exceptions used in the movie-actor dataset processing.

Currently included exceptions:
- ActorNotFoundError: Raised when a specified actor is not found in the dataset.

Usage example:
    from exceptions import ActorNotFoundError

    def find_actor(dataset, actor_name: str):
        if actor_name not in dataset:
            raise ActorNotFoundError(actor_name)
"""


class ActorNotFoundError(Exception):
    """Exception raised when a specified actor is not found in the dataset.

    Attributes:
        actor_name (str): The name of the actor that was not found.
    """

    def __init__(self, actor_name: str):
        """Initializes the ActorNotFoundError.

        Args:
            actor_name (str): The name of the actor that could not be found.
        """
        self.actor_name = actor_name

    def __str__(self):
        """Returns:
        str: A user-friendly error message.
        """
        return f"Actor '{self.actor_name}' wasn't found!"
