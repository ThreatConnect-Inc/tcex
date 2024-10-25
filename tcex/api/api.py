"""TcEx Framework Module"""

# third-party
from requests import Session  # TYPE-CHECKING

# first-party
from tcex.api.tc.tc import TC
from tcex.input.input import Input  # TYPE-CHECKING
from tcex.pleb.cached_property import cached_property


class API:
    """API

    Args:
        inputs: An instance of the Input class.
        session_tc: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, inputs: Input, session_tc: Session):
        """Initialize instance properties."""
        self.inputs = inputs
        self.session_tc = session_tc

    @cached_property
    def tc(self) -> TC:
        """Return a case management instance."""
        return TC(self.inputs, self.session_tc)
