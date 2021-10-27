"""Session singleton"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.sessions.tc_session import TcSession

if TYPE_CHECKING:
    # first-party
    from tcex.input.field_types.sensitive import Sensitive


class Singleton(type):
    """A singleton Metaclass"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Evoke call method."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class TcSessionSingleton(metaclass=Singleton):
    """ThreatConnect Session Singleton Class.

    For Playbook and Organization (Job) Apps an API token will always be provided with
    an expiration time. There will always only be one token provided, however this
    token will need to be renewed.
    """

    def __init__(self, base_url: str, tc_token: 'Sensitive', tc_token_expires: int) -> None:
        """Initialize class properties."""
        # TODO: [high] how to handle token renewal?
        self.tc_token_expires = tc_token_expires

        # properties
        self.session = TcSession(None, None, base_url)
        self.session.token = tc_token.value
