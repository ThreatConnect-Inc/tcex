"""Session singleton"""
# standard library
from typing import TYPE_CHECKING, Optional

# first-party
from tcex.pleb.singleton import Singleton
from tcex.sessions.tc_session import TcSession
from tcex.tokens import Tokens

if TYPE_CHECKING:
    # first-party
    from tcex.input.field_types.sensitive import Sensitive


class TcSessionSingleton(metaclass=Singleton):
    """ThreatConnect Session Singleton Class.

    For Playbook and Organization (Job) Apps an API token will always be provided with
    an expiration time. There will only be one token provided for these App types,
    however this token will need to be renewed.
    """

    def __init__(
        self,
        base_url: str,
        tc_token: 'Sensitive',
        tc_token_expires: int,
        verify: Optional[bool] = True,
    ) -> None:
        """Initialize class properties."""
        self.tc_token_expires = tc_token_expires

        # properties
        self.session = TcSession(None, None, base_url)
        # self.session.token = tc_token.value
        self.session.verify = verify

        # register token
        _tokens = Tokens(token_url=base_url, verify=verify)
        _tokens.register_token(
            key='tc_session_singleton',
            token=tc_token.value,
            expires=tc_token_expires,
        )

        # add token module for auth
        self.session.token = _tokens
