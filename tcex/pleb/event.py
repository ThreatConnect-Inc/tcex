"""Event"""


class Singleton(type):
    """A singleton Metaclass"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Evoke call method."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Event(metaclass=Singleton):
    """Event Class"""

    def __init__(self):
        """."""
        self.channels = {}

    def send(self, channel: str, **kwargs) -> None:
        """Send message to channel."""
        for callback in self.channels.get(channel, []):
            callback(**kwargs)

    def subscribe(self, channel: str, callback: callable):
        """Subscribe to a channel with a callback."""
        self.channels.setdefault(channel, [])
        self.channels[channel].append(callback)

    def unsubscribe(self, channel: str, callback: callable):
        """Subscribe to a channel with a callback."""
        self.channels[channel].remove(callback)
