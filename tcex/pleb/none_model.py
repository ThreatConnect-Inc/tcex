"""None Model"""


class Singleton(type):
    """A singleton Metaclass"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Evoke call method."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class NoneModel(metaclass=Singleton):
    """A dummy model that return None for all attribute requests."""

    def __getattribute__(self, name: str):
        """Return None for any attribute request."""
        return None
