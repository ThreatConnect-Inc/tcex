# -*- coding: utf-8 -*-
"""TcEx Framework Logger module"""
import logging
from logging.handlers import RotatingFileHandler
import os
import platform
import sys
import time
from inspect import getframeinfo, stack


# Create trace logging
logging.TRACE = logging.DEBUG - 5
logging.addLevelName(logging.TRACE, 'TRACE')


class TraceLogger(logging.Logger):
    """Add trace level to logging"""

    _in_trace = False

    def findCaller(self, stack_info=False):
        """Find the caller for the current log event."""
        caller = None
        depth = 3
        while True:
            # search for the correct calling method
            caller = getframeinfo(stack()[depth][0])
            if caller.function != 'trace' or depth >= 6:
                break
            depth += 1

        if sys.version_info < (3,):
            # return value for py2
            return (caller.filename, caller.lineno, caller.function)
        return (caller.filename, caller.lineno, caller.function, None)

    def trace(self, msg, *args, **kwargs):
        """Set trace logging level"""
        self.log(logging.TRACE, msg, *args, **kwargs)


class TcExLogger(object):
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

    # @property
    # def _formatter(self):
    #     """Return log formatter."""
    #     tx_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
    #     tx_format += '(%(filename)s:%(funcName)s:%(lineno)d)'
    #     return logging.Formatter(tx_format)

    @property
    def log(self):
        """Return logger."""
        return self._logger

    @property
    def logging_level(self):
        """Return the configured logging level."""
        level = logging.DEBUG
        if self.tcex.default_args.logging is not None:
            level = logging.getLevelName(self.tcex.default_args.logging.upper())
        elif self.tcex.default_args.tc_log_level is not None:
            level = logging.getLevelName(self.tcex.default_args.tc_log_level.upper())
        return level

    def remove_handler_by_name(self, handler_name):
        """Remove a file handler by name."""
        for h in self._logger.handlers:
            if h.get_name() == handler_name:
                self._logger.removeHandler(h)
                break

    def update_handler_level(self, level=None):
        """Remove a file handler by name."""
        updated_level = self.logging_level
        if level is not None:
            updated_level = logging.getLevelName(level.upper())
        for h in self._logger.handlers:
            h.setLevel(updated_level)

    #
    # handlers
    #

    def add_api_handler(self, name='api'):
        """Add API logging handler."""
        self.remove_handler_by_name(name)
        api = ApiHandler(self.tcex.session)
        api.set_name(name)
        api.setLevel(self.logging_level)
        api.setFormatter(ApiFormatter())
        self._logger.addHandler(api)

    def add_file_handler(self, name='fh', filename=None, formatter=None, level=None):
        """Add File logging handler."""
        self.remove_handler_by_name(name)
        filename = filename or self.tcex.default_args.tc_log_file
        formatter = formatter or FileHandleFormatter()
        level = level or self.logging_level
        # create customized handler
        fh = FileHandlerCustom(os.path.join(self.tcex.default_args.tc_log_path, filename))
        fh.set_name(name)
        fh.setFormatter(formatter)
        fh.setLevel(level)
        self._logger.addHandler(fh)

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
        """Return rotating file handler."""
        self.remove_handler_by_name(name)
        backup_count = backup_count or self.tcex.default_args.tc_log_backup_count
        filename = filename or self.tcex.default_args.tc_log_file
        formatter = formatter or FileHandleFormatter()
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
        """Return stream logging handler."""
        self.remove_handler_by_name(name)
        formatter = formatter or FileHandleFormatter()
        level = level or self.logging_level
        # create handler
        sh = logging.StreamHandler()
        sh.set_name(name)
        sh.setFormatter(formatter)
        sh.setLevel(level)
        self._logger.addHandler(sh)

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
        if self.tcex.install_json:
            app_commit_hash = self.tcex.install_json.get('commitHash')
            app_features = ','.join(self.tcex.install_json.get('features', []))
            app_min_ver = self.tcex.install_json.get('minServerVersion', 'N/A')
            app_name = self.tcex.install_json.get('displayName')
            app_runtime_level = self.tcex.install_json.get('runtimeLevel')
            app_version = self.tcex.install_json.get('programVersion')

            self.log.info('App Name: {}'.format(app_name))
            if app_features:
                self.log.info('App Features: {}'.format(app_features))
            self.log.info('App Minimum ThreatConnect Version: {}'.format(app_min_ver))
            self.log.info('App Runtime Level: {}'.format(app_runtime_level))
            self.log.info('App Version: {}'.format(app_version))
            if app_commit_hash is not None:
                self.log.info('App Commit Hash: {}'.format(app_commit_hash))

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


class ApiFormatter(logging.Formatter):
    """Logger formatter for ThreatConnect Exchange API logging."""

    def __init__(self, task_name=None):
        """Initialize Class properties."""
        self.task_name = task_name
        super(ApiFormatter, self).__init__()

    def format(self, record):
        """Format log record for ThreatConnect API.

        Example log event::

            [{
                "timestamp": 1478907537000,
                "message": "Test Message",
                "level": "DEBUG"
            }]
        """
        return {
            'timestamp': int(float(record.created or time.time()) * 1000),
            'message': record.msg or '',
            'level': record.levelname or 'DEBUG',
        }


class ApiHandler(logging.Handler):
    """Logger handler for ThreatConnect Exchange API logging."""

    def __init__(self, session, flush_limit=100):
        """Initialize Class properties.

        Args:
            session (Request.Session): The preconfigured instance of Session for ThreatConnect API.
            flush_limit (int): The limit to flush batch logs to the API.
        """
        super(ApiHandler, self).__init__()
        self.session = session
        self.flush_limit = flush_limit
        self.entries = []

    def close(self):
        """Close the logger and flush entries."""
        self.log_to_api()
        self.entries = []

    def emit(self, record):
        """Emit the log record."""
        self.entries.append(self.format(record))
        if len(self.entries) > self.flush_limit and not self.session.auth.renewing:
            self.log_to_api()
            self.entries = []

    def log_to_api(self):
        """Best effort API logger.

        Send logs to the ThreatConnect API and do nothing if the attempt fails.
        """
        if self.entries:
            try:
                headers = {'Content-Type': 'application/json'}
                self.session.post('/v2/logs/app', headers=headers, json=self.entries)
                # self.entries = []  # clear entries
            except Exception:
                # best effort on api logging
                pass


class FileHandlerCustom(logging.FileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        """Add logic to create log directory if it does not exists."""
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)


class FileHandleFormatter(logging.Formatter):
    """Logger formatter for ThreatConnect Exchange file handler logging."""

    standard_format = (
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
        '(%(filename)s:%(funcName)s:%(lineno)d:%(thread)d)'
    )
    trace_format = (
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] %(message)s '
        '(%(filename)s:%(thread)d)'
    )

    def __init__(self):
        """Initialize formatter parent."""
        try:  # py3
            super(FileHandleFormatter, self).__init__(
                fmt='%(levelno)d: %(msg)s', datefmt=None, style='%'
            )
        except TypeError:  # py2
            # TODO: remove after py2 support is dropped
            super(FileHandleFormatter, self).__init__(fmt='%(levelno)d: %(msg)s', datefmt=None)

    def format(self, record):
        """Format file handle log event according to logging level."""

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno in [logging.DEBUG, logging.TRACE]:
            self._style._fmt = FileHandleFormatter.trace_format
        else:
            self._style._fmt = FileHandleFormatter.standard_format

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


class RotatingFileHandlerCustom(RotatingFileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        """Add logic to create log directory if it does not exists."""
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

    # TODO: investigate controlling logging thread events
    # def emit(self, record):
    #     """Emit the log record."""
    #     self.reopenIfNeeded()
    #     print(self.name)
    #     logging.FileHandler.emit(self, record)
