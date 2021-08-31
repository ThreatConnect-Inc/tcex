"""Case Management"""
# third-party
from requests import Session

# first-party
# from tcex.api.v2 import V2
from tcex.api.v3.v3 import V3


class API:
    """Case Management

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session) -> None:
        """Initialize Class properties."""
        self.session = session

    # @property
    # def v2(self) -> V2:
    #     """Return a instance of Adversary object."""
    #
    #     return V2(self.session)

    @property
    def v3(self) -> V3:
        """Return a instance of Adversary object."""

        return V3(self.session)
