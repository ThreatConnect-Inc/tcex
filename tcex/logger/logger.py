# -*- coding: utf-8 -*-
"""TcEx Framework Logger module"""
# standard library
import logging
import os
import pathlib
import platform
import sys

from .api_handler import ApiHandler, ApiHandlerFormatter
from .cache_handler import CacheHandler
from .rotating_file_handler_custom import RotatingFileHandlerCustom
from .thread_file_handler import ThreadFileHandler
from .trace_logger import TraceLogger


class Logger:
    """Framework logger module."""

    def __init__(self, tcex, logger_name):
        """Initialize Class Properties.

        Args:
            tcex (tcex.TcEx): Instance of TcEx class.
            logger_name (str): The name of the logger.
        """
        self.tcex = tcex
        self.logger_name = logger_name

    @property
    def _logger(self):
        """Return the logger. The default_args property is not available in init."""
        logging.setLoggerClass(TraceLogger)
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.TRACE)
        return logger

    @property
    def _formatter(self):
        """Return log formatter."""
        tx_format = (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
            '(%(filename)s:%(funcName)s:%(lineno)d)'
        )
        return logging.Formatter(tx_format)

    @property
    def _formatter_thread_name(self):
        """Return log formatter."""
        tx_format = (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
            '(%(filename)s:%(funcName)s:%(lineno)d:%(threadName)s)'
        )
        return logging.Formatter(tx_format)

    @property
    def log(self):
        """Return logger."""
        return self._logger

    @staticmethod
    def log_level(level):
        """Return proper level from string.

        Args:
            level (str): The logging level. Default to 'debug'.
        """
        level = level or 'debug'
        return logging.getLevelName(level.upper())

    def remove_handler_by_name(self, handler_name):
        """Remove a file handler by name.

        Args:
            handler_name (str): The handler name to remove.
        """
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                self._logger.removeHandler(h)
                break

    def replay_cached_events(self, handler_name='cache'):
        """Replay cached log events and remove handler."""
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                events = h.events
                self._logger.removeHandler(h)
                for event in events:
                    self._logger.handle(event)
                break

    def shutdown(self):
        """Close all handlers.

        Args:
            handler_name (str): The handler name to remove.
        """
        for h in self._logger.handlers:
            self._logger.removeHandler(h)

    def update_handler_level(self, level):
        """Update all handlers log level.

        Args:
            level (int, optional): The logging level. Defaults to None.
        """
        level = self.log_level(level)

        # update all handler logging levels
        for h in self._logger.handlers:
            h.setLevel(level)

    #
    # handlers
    #

    def add_api_handler(self, name='api', level=None):
        """Add API logging handler.

        Args:
            name (str, optional): The name of the handler. Defaults to 'api'.
            level (str, optional): The level value as a string. Defaults to None.
        """
        self.remove_handler_by_name(name)
        api = ApiHandler(self.tcex.session)
        api.set_name(name)
        api.setLevel(self.log_level(level))
        api.setFormatter(ApiHandlerFormatter())
        self._logger.addHandler(api)

    def add_cache_handler(self, name):
        """Add cache logging handler.

        Args:
            name (str): The name of the handler.
        """
        self.remove_handler_by_name(name)
        cache = CacheHandler()
        cache.set_name(name)
        # set logging level to INFO as event will typically be only those that happen before args
        # are processed
        cache.setLevel(self.log_level('trace'))
        cache.setFormatter(self._formatter)
        self._logger.addHandler(cache)

    def add_rotating_file_handler(
        self, name, filename, path, backup_count, max_bytes, level, formatter=None, mode='a'
    ):
        """Add a rotating file handler

        Args:
            name (str, optional): The name of the handler. Defaults to 'rfh'.
            filename (str): The name of the logfile.
            path (str): The path for the logfile.
            backup_count (int, optional): The maximum # of backup files. Defaults to 0.
            max_bytes (int): The max file size before rotating. Defaults to 0.
            level (str): The logging level. Defaults to None.
            formatter (str, optional): The logging formatter to use. Defaults to None.
            mode (str, optional): The write mode for the file. Defaults to 'a'.
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

    def add_stream_handler(self, name='sh', formatter=None, level=None):
        """Return stream logging handler.

        Args:
            name (str, optional): The name of the handler. Defaults to 'sh'.
            formatter (str, optional): The logging formatter to use. Defaults to None.
            level (int, optional): The logging level. Defaults to None.
        """
        self.remove_handler_by_name(name)
        formatter = formatter or self._formatter
        # create handler
        sh = logging.StreamHandler()
        sh.set_name(name)
        sh.setFormatter(formatter)
        sh.setLevel(self.log_level(level))
        self._logger.addHandler(sh)

    def add_thread_file_handler(self, name, filename, level, path, formatter=None):
        """Add File logging handler.

        Args:
            name (str): The name of the handler.
            filename (str): The name of the logfile.
            level (int, optional): The logging level. Defaults to None.
            path (str): The path for the logfile.
            formatter (str, optional): The logging formatter to use. Defaults to None.
        """
        self.remove_handler_by_name(name)
        formatter = formatter or self._formatter
        # create customized handler
        fh = ThreadFileHandler(os.path.join(path, filename))
        fh.set_name(name)
        fh.setFormatter(formatter)
        fh.setLevel(self.log_level(level))
        self._logger.addHandler(fh)

    #
    # App info logging
    #

    def log_info(self, args):
        """Send System and App data to logs."""
        self._log_platform()
        self._log_app_data()
        self._log_python_version()
        self._log_tcex_version()
        self._log_tcex_path()
        self._log_tc_proxy(args)

    def _log_app_data(self):
        """Log the App data information."""
        # Best Effort
        try:
            self.log.info(f'App Name: {self.tcex.ij.display_name}')
            if self.tcex.ij.features:
                self.log.info(f"App Features: {','.join(self.tcex.ij.features)}")
            self.log.info(f'App Minimum ThreatConnect Version: {self.tcex.ij.min_server_version}')
            self.log.info(f'App Runtime Level: {self.tcex.ij.runtime_level}')
            self.log.info(f'App Version: {self.tcex.ij.program_version}')
            if self.tcex.ij.commit_hash is not None:
                self.log.info(f'App Commit Hash: {self.tcex.ij.commit_hash}')
        except Exception:  # nosec; pragma: no cover
            pass

    def _log_platform(self):
        """Log the current Platform."""
        self.log.info(f'Platform: {platform.platform()}')

    def _log_python_version(self):
        """Log the current Python version."""
        self.log.info(
            f'Python Version: {sys.version_info.major}.'
            f'{sys.version_info.minor}.'
            f'{sys.version_info.micro}'
        )

    def _log_tc_proxy(self, args):
        """Log the proxy settings."""
        if args.tc_proxy_tc:
            self.log.info(f'Proxy Server (TC): {args.tc_proxy_host}:{args.tc_proxy_port}.')

    def _log_tcex_version(self):
        """Log the current TcEx version number."""
        self.log.info(f'TcEx Version: {__import__(__name__).__version__}')

    def _log_tcex_path(self):
        """Log the current TcEx path."""
        app_path = str(pathlib.Path().parent.absolute())
        full_path = str(pathlib.Path(__file__).parent.absolute())
        tcex_path = os.path.dirname(full_path.replace(app_path, ''))
        self.log.info(f'TcEx Path: {tcex_path}')
