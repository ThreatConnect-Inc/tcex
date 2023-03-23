"""TcEx Module"""
# standard library
import logging

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.input.model.module_requests_session_model import ModuleRequestsSessionModel
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property
from tcex.pleb.proxies import proxies
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

    def __init__(self, model: ModuleRequestsSessionModel):
        """Initialize instance properties."""
        self.model = model

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
        if self.model.tc_proxy_external:
            _session_external.proxies = self.proxies
            self.log.info(
                f'Using proxy host {self.model.tc_proxy_host}:'
                f'{self.model.tc_proxy_port} for external session.'
            )

        if self.model.tc_log_curl:
            _session_external.log_curl = log_curl

        return _session_external

    def get_session_tc(
        self,
        auth: HmacAuth | TokenAuth | TcAuth | None = None,
        base_url: str | None = None,
        log_curl: bool | None = None,
        proxies_: dict[str, str] | None = None,
        proxies_enabled: bool | None = None,
        verify: bool | str | None = None,
    ) -> TcSession:
        """Return an instance of Requests Session configured for the ThreatConnect API.

        No args are required to get a working instance of TC Session instance.

        This method allows for getting a new instance of TC Session instance. This can be
        very useful when connecting between multiple TC instances (e.g., migrating data).
        """
        if log_curl is None:
            log_curl = self.model.tc_log_curl

        if proxies_enabled is None:
            proxies_enabled = self.model.tc_proxy_tc

        if verify is None:
            verify = self.model.tc_verify

        token_callable = registry.app.token.get_token
        if self.install_json.is_external_app is True:
            token_callable = None

        auth = auth or TcAuth(
            tc_api_access_id=self.model.tc_api_access_id,
            tc_api_secret_key=self.model.tc_api_secret_key,
            tc_token=token_callable,
        )

        return TcSession(
            auth=auth,
            base_url=base_url or self.model.tc_api_path,
            log_curl=log_curl,
            proxies=proxies_ or self.proxies,
            proxies_enabled=proxies_enabled,
            user_agent=registry.app.user_agent,
            verify=verify,
        )

    @cached_property
    def proxies(self) -> dict:
        """Return proxies dictionary for use with the Python Requests module."""
        return proxies(
            proxy_host=self.model.tc_proxy_host,
            proxy_port=self.model.tc_proxy_port,
            proxy_user=self.model.tc_proxy_username,
            proxy_pass=self.model.tc_proxy_password,
        )

    @scoped_property
    def tc(self) -> TcSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session_tc()
