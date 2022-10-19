"""API"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc import TC
from tcex.backports import cached_property

if TYPE_CHECKING:
    # third-party
    from requests import Session

    # first-party
    from tcex.input.input import Input


class API:
    """API

    Args:
        inputs: An instance of the Input class.
        session_tc: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, inputs: 'Input', session_tc: 'Session'):
        """Initialize Class properties."""
        self.inputs = inputs
        self.session_tc = session_tc

    @cached_property
    def tc(self) -> 'TC':
        """Return a case management instance."""
        return TC(self.inputs, self.session_tc)
