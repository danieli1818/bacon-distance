class ActorNotFoundError(Exception):
    """
    This error is raised when an actor wasn't found.
    """

    def __init__(self, actor_name: str):
        self.actor_name = actor_name

    def __str__(self):
        return f"Actor '{self.actor_name}' wasn't found!"
