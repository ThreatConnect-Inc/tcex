"""TcEx Framework Module"""

# standard library
import logging
import os
import platform
import sys
from importlib.metadata import version
from pathlib import Path
from urllib.parse import urlsplit

# third-party
from certifi import where
from requests import Session  # TYPE-CHECKING

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.input.model.common_model import CommonModel  # TYPE-CHECKING
from tcex.logger.api_handler import ApiHandler, ApiHandlerFormatter
from tcex.logger.cache_handler import CacheHandler
from tcex.logger.rotating_file_handler_custom import RotatingFileHandlerCustom
from tcex.logger.trace_logger import TraceLogger


class Logger:
    """Framework logger module."""

    def __init__(self, logger_name: str):
        """Initialize instance properties."""
        self.logger_name = logger_name

        # properties
        self.ij = InstallJson()

    @property
    def _logger(self) -> TraceLogger:
        """Return the logger. The inputs.model property is not available in init."""
        logging.setLoggerClass(TraceLogger)
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.TRACE)  # type: ignore
        return logger  # type: ignore

    @property
    def _formatter(self) -> logging.Formatter:
        """Return log formatter."""
        tx_format = (
            '%(asctime)s - %(name)s - %(levelname)8s - %(message)s '
            '(%(filename)s:%(funcName)s:%(lineno)d)'
        )
        return logging.Formatter(tx_format)

    @property
    def _formatter_thread_name(self) -> logging.Formatter:
        """Return log formatter."""
        tx_format = (
            '%(asctime)s - %(name)s - %(levelname)8s - %(message)s '
            '(%(filename)s:%(funcName)s:%(lineno)d:%(threadName)s)'
        )
        return logging.Formatter(tx_format)

    def handler_exist(self, handler_name: str) -> bool:
        """Remove a file handler by name.

        Args:
            handler_name: The handler name to remove.

        Returns:
            bool: True if handler current exists
        """
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                return True
        return False

    @property
    def log(self) -> TraceLogger:
        """Return logger."""
        return self._logger

    @staticmethod
    def log_level(level: str | None) -> int:
        """Return proper level from string.

        Args:
            level: The logging level.

        Returns:
            int: The logging level as an int.
        """
        level = level or 'debug'
        return logging.getLevelName(level.upper())

    def remove_handler_by_name(self, handler_name: str):
        """Remove a file handler by name.

        Args:
            handler_name: The handler name to remove.
        """
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                self._logger.removeHandler(h)
                break

    def replay_cached_events(self, handler_name: str = 'cache'):
        """Replay cached log events and remove handler."""
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                events = h.events  # type: ignore
                self._logger.removeHandler(h)
                for event in events:
                    self._logger.handle(event)
                break

        # remove the cache handler
        self.remove_handler_by_name(handler_name=handler_name)

    def shutdown(self):
        """Close all handlers.

        Args:
            handler_name (str): The handler name to remove.
        """
        for h in self._logger.handlers:
            self._logger.removeHandler(h)

    def update_handler_level(self, level: str):
        """Update all handlers log level.

        Args:
            level: The logging level.
        """
        level_ = self.log_level(level)

        # update all handler logging levels
        for h in self._logger.handlers:
            h.setLevel(level_)

    #
    # handlers
    #

    def add_api_handler(self, session_tc: Session, name: str = 'api', level: str | None = None):
        """Add API logging handler.

        Args:
            session_tc: An configured instance of request.Session with TC API Auth.
            name: The name of the handler.
            level: The level value as a string.
        """
        self.remove_handler_by_name(name)
        api = ApiHandler(session_tc)
        api.set_name(name)
        api.setLevel(self.log_level(level))
        api.setFormatter(ApiHandlerFormatter())
        self._logger.addHandler(api)

    def add_cache_handler(self, name: str):
        """Add cache logging handler.

        Args:
            name: The name of the handler.
        """
        self.remove_handler_by_name(name)
        cache = CacheHandler()
        cache.set_name(name)
        # set logging level to INFO as event will typically
        # be only those that happen before args are processed
        cache.setLevel(self.log_level('trace'))
        cache.setFormatter(self._formatter)
        self._logger.addHandler(cache)

    def add_rotating_file_handler(
        self,
        name: str,
        filename: str,
        path: Path | str,
        backup_count: int,
        max_bytes: int,
        level: str,
        formatter: logging.Formatter | None = None,
        mode: str = 'a',
    ):
        """Add custom file logging handler.

        Args:
            name: The name of the handler.
            filename: The name of the logfile.
            path: The path for the logfile.
            backup_count: The maximum # of backup files.
            max_bytes: The max file size before rotating.
            level: The logging level.
            formatter: The logging formatter to use.
            mode: The write mode for the file.
        """
        self.remove_handler_by_name(name)
        formatter = formatter or self._formatter_thread_name

        # create customized handler
        fh = RotatingFileHandlerCustom(
            os.path.join(path, filename), backupCount=backup_count, maxBytes=max_bytes, mode=mode
        )
        fh.set_name(name)
        fh.setFormatter(formatter)
        fh.setLevel(self.log_level(level))
        self._logger.addHandler(fh)

    def add_stream_handler(
        self,
        name: str = 'sh',
        formatter: logging.Formatter | None = None,
        level: str | None = None,
    ):
        """Add stream logging handler.

        Args:
            name: The name of the handler.
            formatter: The logging formatter to use.
            level: The logging level.
        """
        self.remove_handler_by_name(name)
        formatter = formatter or self._formatter
        # create handler
        sh = logging.StreamHandler()
        sh.set_name(name)
        sh.setFormatter(formatter)
        sh.setLevel(self.log_level(level))
        self._logger.addHandler(sh)

    #
    # App info logging
    #

    def log_info(self, inputs: CommonModel):
        """Send System and App data to logs.

        Args:
            inputs: The inputs model.
        """
        self._log_app_data()
        self._log_platform()
        self._log_python_version()
        self._log_environment()
        self._log_tcex_version()
        self._log_tc_proxy(inputs)

    def _log_app_data(self):
        """Log the App data information as a best effort."""
        try:
            self.log.info(f'app-name="{self.ij.model.display_name}"')
            if self.ij.model.app_id is not None:
                self.log.info(f'app-id={self.ij.model.app_id}')
            if self.ij.model.features:
                self.log.info(f'''app-features={','.join(self.ij.model.features)}''')
            self.log.info(f'app-minimum-threatconnect-version={self.ij.model.min_server_version}')
            self.log.info(f'app-runtime-level={self.ij.model.runtime_level}')
            app_version = f'app-version={self.ij.model.program_version}'
            if self.ij.model.commit_hash is not None:
                app_version += f', app-commit-hash={self.ij.model.commit_hash}'
            self.log.info(app_version)  # version and commit hash
        except Exception:  # nosec; pragma: no cover
            pass

    def _log_environment(self):
        """Log the current environment variables."""
        self.log.info(f'''env-all-proxy={self._sanitize_proxy_url(os.getenv('ALL_PROXY'))}''')
        self.log.info(f'''env-http-proxy={self._sanitize_proxy_url(os.getenv('HTTP_PROXY'))}''')
        self.log.info(f'''env-https-proxy={self._sanitize_proxy_url(os.getenv('HTTPS_PROXY'))}''')
        self.log.info(f'''env-no-proxy={os.getenv('NO_PROXY')}''')
        self.log.info(f'''env-curl-ca-bundle={os.getenv('CURL_CA_BUNDLE')}''')
        self.log.info(f'''env-request-ca-bundle={os.getenv('REQUESTS_CA_BUNDLE')}''')
        self.log.info(f'''env-ssl-cert-file={os.getenv('SSL_CERT_FILE')}''')

        # log certifi where
        self.log.info(f'''certifi-where={where()}''')

    def _log_platform(self):
        """Log the current Platform."""
        self.log.info(f'platform="{platform.platform()}"')
        self.log.info(f'pid={os.getpid()}')

    def _log_python_version(self):
        """Log the current Python version."""
        self.log.info(
            f'python-version={sys.version_info.major}.'
            f'{sys.version_info.minor}.'
            f'{sys.version_info.micro}'
        )

    def _log_tc_proxy(self, inputs: CommonModel):
        """Log the proxy settings.

        Args:
            inputs: The inputs model.
        """
        if inputs.tc_proxy_tc:
            self.log.info(f'proxy-server-tc={inputs.tc_proxy_host}:{inputs.tc_proxy_port}')

    def _log_tcex_version(self):
        """Log the current TcEx version number."""
        try:
            self.log.info(f'''tcex-version={version('tcex')}''')
        except ImportError:
            self.log.warning('TcEx version no found.')

    @staticmethod
    def _sanitize_proxy_url(url: str | None) -> str | None:
        """Sanitize a proxy url, masking username and password."""
        if url is not None:
            url_data = urlsplit(url)
            if all([url_data.username, url_data.password]):
                url = url.replace(f'{url_data.username}:{url_data.password}', '***:***')
        return url
