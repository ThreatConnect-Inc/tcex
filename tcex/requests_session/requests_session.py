"""TcEx Module"""
# standard library
import logging

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.backport import cached_property
from tcex.input.input import Input
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module
from tcex.pleb.registry import registry
from tcex.pleb.scoped_property import scoped_property
from tcex.requests_session.auth.hmac_auth import HmacAuth
from tcex.requests_session.auth.tc_auth import TcAuth
from tcex.requests_session.auth.token_auth import TokenAuth
from tcex.requests_session.external_session import ExternalSession
from tcex.requests_session.tc_session import TcSession

# get tcex logger
logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


class RequestsSession:
    """TcEx Module"""

    def __init__(self, inputs: Input, proxies: dict[str, str]):
        """Initialize Class properties."""
        self.inputs = inputs
        self.proxies = proxies

        # properties
        self.install_json = InstallJson()
        self.log = logger

    @cached_property
    def external(self) -> ExternalSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session_external()

    def get_session_external(self, log_curl: bool = True) -> ExternalSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        _session_external = ExternalSession()

        # add User-Agent to headers
        _session_external.headers.update(registry.app.user_agent)

        # add proxy support if requested
        if self.inputs.model_unresolved.tc_proxy_external:
            _session_external.proxies = self.proxies
            self.log.info(
                f'Using proxy host {self.inputs.model_unresolved.tc_proxy_host}:'
                f'{self.inputs.model_unresolved.tc_proxy_port} for external session.'
            )

        if self.inputs.model_unresolved.tc_log_curl:
            _session_external.log_curl = log_curl

        return _session_external

    def get_session_tc(
        self,
        auth: HmacAuth | TokenAuth | TcAuth | None = None,
        base_url: str | None = None,
        log_curl: bool | None = None,
        proxies: dict[str, str] | None = None,  # pylint: disable=redefined-outer-name
        proxies_enabled: bool | None = None,
        verify: bool | str | None = None,
    ) -> TcSession:
        """Return an instance of Requests Session configured for the ThreatConnect API.

        No args are required to get a working instance of TC Session instance.

        This method allows for getting a new instance of TC Session instance. This can be
        very useful when connecting between multiple TC instances (e.g., migrating data).
        """
        if log_curl is None:
            log_curl = self.inputs.model_unresolved.tc_log_curl

        if proxies_enabled is None:
            proxies_enabled = self.inputs.model_unresolved.tc_proxy_tc

        if verify is None:
            verify = self.inputs.model_unresolved.tc_verify

        token = registry.app.token
        if self.install_json.is_external_app is True:
            token = None

        auth = auth or TcAuth(
            tc_api_access_id=self.inputs.model_unresolved.tc_api_access_id,
            tc_api_secret_key=self.inputs.model_unresolved.tc_api_secret_key,
            tc_token=token,
        )

        return TcSession(
            auth=auth,
            base_url=base_url or self.inputs.model_unresolved.tc_api_path,
            log_curl=log_curl,
            proxies=proxies or self.proxies,
            proxies_enabled=proxies_enabled,
            user_agent=registry.app.user_agent,
            verify=verify,
        )

    @scoped_property
    def tc(self) -> TcSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session_tc()
