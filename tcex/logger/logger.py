"""TcEx Framework Logger module"""
# standard library
import logging
import os
import pathlib
import platform
import sys
from typing import Optional

from .api_handler import ApiHandler, ApiHandlerFormatter
from .cache_handler import CacheHandler
from .pattern_file_handler import PatternFileHandler
from .rotating_file_handler_custom import RotatingFileHandlerCustom
from .sensitive_filter import SensitiveFilter
from .thread_file_handler import ThreadFileHandler
from .trace_logger import TraceLogger


class Logger:
    """Framework logger module."""

    def __init__(self, tcex: object, logger_name: str):
        """Initialize Class Properties.

        Args:
            tcex: Instance of TcEx class.
            logger_name: The name of the logger.
        """
        self.tcex = tcex
        self.logger_name = logger_name
        self.filter_sensitive = SensitiveFilter(name='sensitive_filter')

    @property
    def _logger(self) -> logging.Logger:
        """Return the logger. The default_args property is not available in init."""
        logging.setLoggerClass(TraceLogger)
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.TRACE)
        logger.addFilter(self.filter_sensitive)
        return logger

    @property
    def _formatter(self) -> None:
        """Return log formatter."""
        tx_format = (
            '%(asctime)s - %(name)s - %(levelname)8s - %(message)s '
            '(%(filename)s:%(funcName)s:%(lineno)d)'
        )
        return logging.Formatter(tx_format)

    @property
    def _formatter_thread_name(self) -> None:
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
    def log(self) -> logging.Logger:
        """Return logger."""
        return self._logger

    @staticmethod
    def log_level(level: str) -> int:
        """Return proper level from string.

        Args:
            level: The logging level.

        Returns:
            int: The logging level as an int.
        """
        level = level or 'debug'
        return logging.getLevelName(level.upper())

    def remove_handler_by_name(self, handler_name: str) -> None:
        """Remove a file handler by name.

        Args:
            handler_name: The handler name to remove.
        """
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                self._logger.removeHandler(h)
                break

    def replay_cached_events(self, handler_name: Optional[str] = 'cache') -> None:
        """Replay cached log events and remove handler."""
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                events = h.events
                self._logger.removeHandler(h)
                for event in events:
                    self._logger.handle(event)
                break

    def shutdown(self) -> None:
        """Close all handlers.

        Args:
            handler_name (str): The handler name to remove.
        """
        for h in self._logger.handlers:
            self._logger.removeHandler(h)

    def update_handler_level(self, level: int) -> None:
        """Update all handlers log level.

        Args:
            level: The logging level.
        """
        level = self.log_level(level)

        # update all handler logging levels
        for h in self._logger.handlers:
            h.setLevel(level)

    #
    # handlers
    #

    def add_api_handler(self, name: Optional[str] = 'api', level: Optional[str] = None) -> None:
        """Add API logging handler.

        Args:
            name: The name of the handler.
            level: The level value as a string.
        """
        self.remove_handler_by_name(name)
        api = ApiHandler(self.tcex.session)
        api.set_name(name)
        api.setLevel(self.log_level(level))
        api.setFormatter(ApiHandlerFormatter())
        self._logger.addHandler(api)

    def add_cache_handler(self, name: str) -> None:
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

    def add_pattern_file_handler(
        self,
        name: str,
        filename: str,
        level: int,
        path: str,
        pattern: str,
        formatter: Optional[str] = None,
        handler_key: Optional[str] = None,
        max_log_count: Optional[int] = 100,
        thread_key: Optional[str] = None,
    ) -> None:
        """Add custom file logging handler.

        This handler is intended for service Apps that need to log events based on the
        current session id. All log event would be in context to a single playbook execution.

        Args:
            name: The name of the handler.
            filename: The name of the logfile.
            level: The logging level.
            path: The path for the logfile.
            formatter: The logging formatter to use.
            handler_key: Additional properties for handler to thread condition.
            max_log_count: The maximun number of logs to keep that match the provided pattern.
            pattern: The pattern used to match the log files.
            thread_key: Additional properties for handler to thread condition.
        """
        self.remove_handler_by_name(name)
        formatter = formatter or self._formatter
        # create customized handler
        fh = PatternFileHandler(
            filename=os.path.join(path, filename), pattern=pattern, max_log_count=max_log_count
        )
        fh.set_name(name)
        fh.setFormatter(formatter)
        fh.setLevel(self.log_level(level))
        # add keys for halder emit method conditional
        fh.handler_key = handler_key
        fh.thread_key = thread_key
        self._logger.addHandler(fh)

    def add_rotating_file_handler(
        self,
        name: str,
        filename: str,
        path: str,
        backup_count: int,
        max_bytes: int,
        level: str,
        formatter: Optional[str] = None,
        mode: Optional[str] = 'a',
    ) -> None:
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
        name: Optional[str] = 'sh',
        formatter: Optional[str] = None,
        level: Optional[int] = None,
    ) -> None:
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

    def add_thread_file_handler(
        self,
        name: str,
        filename: str,
        level: str,
        path: str,
        backup_count: Optional[int] = 0,
        formatter: Optional[str] = None,
        handler_key: Optional[str] = None,
        max_bytes: Optional[int] = 0,
        mode: Optional[str] = 'a',
        thread_key: Optional[str] = None,
    ) -> None:
        """Add custom file logging handler.

        This handler is intended for service Apps that need to log events based on the
        current trigger id. All log events would be in context to a single playbook.

        Args:
            name: The name of the handler.
            filename: The name of the logfile.
            level: The logging level.
            path: The path for the logfile.
            backup_count: The maximum # of backup files.
            formatter: The logging formatter to use.
            handler_key: Additional properties for handler to thread condition.
            max_bytes: The max file size before rotating.
            mode: The write mode for the file.
            thread_key: Additional properties for handler to thread condition.
        """
        self.remove_handler_by_name(name)
        formatter = formatter or self._formatter_thread_name
        # create customized handler
        fh = ThreadFileHandler(
            os.path.join(path, filename), backupCount=backup_count, maxBytes=max_bytes, mode=mode
        )
        fh.set_name(name)
        fh.setFormatter(formatter)
        fh.setLevel(self.log_level(level))
        # add keys for halder emit method conditional
        fh.handler_key = handler_key
        fh.thread_key = thread_key
        self._logger.addHandler(fh)

    #
    # App info logging
    #

    def log_info(self, args: object) -> None:
        """Send System and App data to logs.

        Args:
            args: The args namespace for App.
        """
        self._log_platform()
        self._log_app_data()
        self._log_python_version()
        self._log_tcex_version()
        self._log_tcex_path()
        self._log_tc_proxy(args)

    def _log_app_data(self) -> None:
        """Log the App data information as a best effort."""
        try:
            self.log.info(f'app-name="{self.tcex.ij.display_name}"')
            if self.tcex.ij.features:
                self.log.info(f'app-features={self.tcex.ij.features}')
            self.log.info(f'app-minimum-threatconnect-version={self.tcex.ij.min_server_version}')
            self.log.info(f'app-runtime-level={self.tcex.ij.runtime_level}')
            self.log.info(f'app-version={self.tcex.ij.program_version}')
            if self.tcex.ij.commit_hash is not None:
                self.log.info(f'app-commit-hash={self.tcex.ij.commit_hash}')
        except Exception:  # nosec; pragma: no cover
            pass

    def _log_platform(self) -> None:
        """Log the current Platform."""
        self.log.info(f'platform="{platform.platform()}"')
        self.log.info(f'pid={os.getpid()}')

    def _log_python_version(self) -> None:
        """Log the current Python version."""
        self.log.info(
            f'python-version={sys.version_info.major}.'
            f'{sys.version_info.minor}.'
            f'{sys.version_info.micro}'
        )

    def _log_tc_proxy(self, args: object) -> None:
        """Log the proxy settings.

        Args:
            args: The args namespace for App.
        """
        if args.tc_proxy_tc:
            self.log.info(f'proxy-server-tc={args.tc_proxy_host}:{args.tc_proxy_port}')

    def _log_tcex_version(self) -> None:
        """Log the current TcEx version number."""
        self.log.info(f'tcex-version={__import__(__name__).__version__}')

    def _log_tcex_path(self) -> None:
        """Log the current TcEx path."""
        app_path = str(pathlib.Path().parent.absolute())
        full_path = str(pathlib.Path(__file__).parent.absolute())
        tcex_path = os.path.dirname(full_path.replace(app_path, ''))
        self.log.info(f'tcex-path="{tcex_path}"')
