"""TcEx Framework Module"""

# standard library
import logging
from functools import cached_property

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.input.model.module_requests_session_model import ModuleRequestsSessionModel
from tcex.registry import registry
from tcex.requests_external.external_session import ExternalSession

# get logger
_logger = logging.getLogger(__name__.split('.', maxsplit=1)[0])


class RequestsExternal:
    """Requests External"""

    def __init__(
        self,
        model: ModuleRequestsSessionModel,
        proxies: dict[str, str],
        user_agent: dict[str, str] | None = None,
    ):
        """Initialize instance properties."""
        self.model = model
        self.proxies = proxies
        self.user_agent = user_agent or registry.app.user_agent

        # properties
        self.install_json = InstallJson()
        self.log = _logger

    def get_session(self, log_curl: bool = True) -> ExternalSession:
        """Return an instance of Requests Session configured for External API requests."""
        _session_external = ExternalSession()

        # add User-Agent to headers
        if self.user_agent:
            _session_external.headers.update(self.user_agent)

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

    @cached_property
    def session(self) -> ExternalSession:
        """Return an instance of Requests Session configured for the ThreatConnect API."""
        return self.get_session()
