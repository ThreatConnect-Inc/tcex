# standard library
import os
from abc import ABC

# third-party
from requests import Session

# first-party
from tcex.input.field_type.sensitive import Sensitive
from tcex.requests_tc.auth.hmac_auth import HmacAuth


class OptionsABC(ABC):  # noqa: B024
    """Abstract base class for all Options classes."""

    def __init__(self, **kwargs):
        """Initialize the OptionsABC class."""
        self._options = kwargs

    @property
    def session(self) -> Session:
        """Return Session configured for TC API."""
        _session = Session()
        _session.auth = HmacAuth(
            os.getenv('TC_API_ACCESS_ID', ''), Sensitive(os.getenv('TC_API_SECRET_KEY', ''))
        )
        return _session
