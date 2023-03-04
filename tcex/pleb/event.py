"""Event"""
# standard library
from collections.abc import Callable

# first-party
from tcex.pleb.singleton import Singleton


class Event(metaclass=Singleton):
    """Event Class"""

    def __init__(self):
        """Initialize Class properties."""
        self.channels = {}

    def send(self, channel: str, **kwargs):
        """Send message to channel."""
        for callback in self.channels.get(channel, []):
            callback(**kwargs)

    def subscribe(self, channel: str, callback: Callable):
        """Subscribe to a channel with a callback."""
        self.channels.setdefault(channel, [])
        self.channels[channel].append(callback)

    def unsubscribe(self, channel: str, callback: Callable):
        """Subscribe to a channel with a callback."""
        self.channels[channel].remove(callback)
