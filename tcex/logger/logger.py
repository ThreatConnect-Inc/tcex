# -*- coding: utf-8 -*-
"""TcEx Framework Logger module"""
import logging
import os
import platform
import sys
from .api_handler import ApiHandler, ApiHandlerFormatter
from .rotating_file_handler_custom import RotatingFileHandlerCustom
from .thread_file_handler import ThreadFileHandler
from .trace_logger import TraceLogger


class Logger(object):
    """Framework logger module."""

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            tcex (tcex.TcEx): Instance of TcEx class.
        """
        self.tcex = tcex

    @property
    def _logger(self):
        """Return the logger. The default_args property is not available in init."""
        logging.setLoggerClass(TraceLogger)
        logger = logging.getLogger(self.tcex.default_args.tc_log_name)
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

    @property
    def logging_level(self):
        """Return the configured logging level."""
        level = 'DEBUG'
        if self.tcex.default_args.logging is not None:
            level = self.tcex.default_args.logging.upper()  # pragma: no cover
        elif self.tcex.default_args.tc_log_level is not None:
            level = self.tcex.default_args.tc_log_level.upper()
        return logging.getLevelName(level)

    def remove_handler_by_name(self, handler_name):
        """Remove a file handler by name.

        Args:
            handler_name (str): The handler name to remove.
        """
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                self._logger.removeHandler(h)
                break

    def update_handler_level(self, level=None):
        """Update all handlers log level.

        Args:
            level (int, optional): The logging level. Defaults to None.
        """
        updated_level = self.logging_level
        if level is not None:
            # if level is not provided get level from args
            updated_level = logging.getLevelName(level.upper())

        # update all handler logging levels
        for h in self._logger.handlers:
            h.setLevel(updated_level)

    #
    # handlers
    #

    def add_api_handler(self, name='api'):
        """Add API logging handler.

        Args:
            name (str, optional): The name of the handler. Defaults to 'api'.
        """
        self.remove_handler_by_name(name)
        api = ApiHandler(self.tcex.session)
        api.set_name(name)
        api.setLevel(self.logging_level)
        api.setFormatter(ApiHandlerFormatter())
        self._logger.addHandler(api)

    def add_rotating_file_handler(
        self,
        name='rfh',
        filename=None,
        level=None,
        formatter=None,
        backup_count=None,
        max_bytes=None,
        mode=None,
    ):
        """Add a rotating file handler

        Args:
            name (str, optional): The name of the handler. Defaults to 'rfh'.
            filename (str): The name of the logfile.
            level (int, optional): The logging level. Defaults to None.
            formatter (str, optional): The logging formatter to use. Defaults to None.
            backupCount (int, optional): The maximum # of backup files. Defaults to 0.
            max_bytes (int, optional): The max file size before rotating. Defaults to 0.
            mode (str, optional): The write mode for the file. Defaults to 'a'.
        """
        self.remove_handler_by_name(name)
        backup_count = backup_count or self.tcex.default_args.tc_log_backup_count
        filename = filename or self.tcex.default_args.tc_log_file
        formatter = formatter or self._formatter_thread_name
        level = level or self.logging_level
        max_bytes = max_bytes or self.tcex.default_args.tc_log_max_bytes
        mode = mode or 'a'
        # create customized handler
        fh = RotatingFileHandlerCustom(
            os.path.join(self.tcex.default_args.tc_log_path, filename),
            backupCount=backup_count,
            maxBytes=max_bytes,
            mode=mode,
        )
        fh.set_name(name)
        fh.setFormatter(formatter)
        fh.setLevel(level)
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
        level = level or self.logging_level
        # create handler
        sh = logging.StreamHandler()
        sh.set_name(name)
        sh.setFormatter(formatter)
        sh.setLevel(level)
        self._logger.addHandler(sh)

    def add_thread_file_handler(self, name='fh', filename=None, formatter=None, level=None):
        """Add File logging handler.

        Args:
            name (str, optional): The name of the handler. Defaults to 'sh'.
            filename (str): The name of the logfile.
            formatter (str, optional): The logging formatter to use. Defaults to None.
            level (int, optional): The logging level. Defaults to None.
        """
        self.remove_handler_by_name(name)
        filename = filename or self.tcex.default_args.tc_log_file
        formatter = formatter or self._formatter
        level = level or self.logging_level
        # create customized handler
        fh = ThreadFileHandler(os.path.join(self.tcex.default_args.tc_log_path, filename))
        fh.set_name(name)
        fh.setFormatter(formatter)
        fh.setLevel(level)
        self._logger.addHandler(fh)

    #
    # App info logging
    #

    def log_info(self):
        """Send System and App data to logs."""
        self._log_platform()
        self._log_app_data()
        self._log_python_version()
        self._log_tcex_version()
        self._log_tc_proxy()

    def _log_app_data(self):
        """Log the App data information."""
        # Best Effort
        try:
            self.log.info('App Name: {}'.format(self.tcex.ij.display_name))
            if self.tcex.ij.features:
                self.log.info('App Features: {}'.format(','.join(self.tcex.ij.features)))
            self.log.info(
                'App Minimum ThreatConnect Version: {}'.format(self.tcex.ij.min_server_version)
            )
            self.log.info('App Runtime Level: {}'.format(self.tcex.ij.runtime_level))
            self.log.info('App Version: {}'.format(self.tcex.ij.program_version))
            if self.tcex.ij.commit_hash is not None:
                self.log.info('App Commit Hash: {}'.format(self.tcex.ij.commit_hash))
        except Exception:
            pass

    def _log_platform(self):
        """Log the current Platform."""
        self.log.info('Platform: {}'.format(platform.platform()))

    def _log_python_version(self):
        """Log the current Python version."""
        self.log.info(
            'Python Version: {}.{}.{}'.format(
                sys.version_info.major, sys.version_info.minor, sys.version_info.micro
            )
        )

    def _log_tc_proxy(self):
        """Log the proxy settings."""
        if self.tcex.default_args.tc_proxy_tc:
            self.log.info(
                'Proxy Server (TC): {}:{}.'.format(
                    self.tcex.default_args.tc_proxy_host, self.tcex.default_args.tc_proxy_port
                )
            )

    def _log_tcex_version(self):
        """Log the current TcEx version number."""
        self.log.info('TcEx Version: {}'.format(__import__(__name__).__version__))
