"""TcEx Framework Module"""

# standard library
import gzip
import os
import shutil
from logging.handlers import RotatingFileHandler


class RotatingFileHandlerCustom(RotatingFileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(
        self,
        filename: str,
        mode: str = 'a',
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: str | None = None,
        delay: bool = False,
    ):
        """Customize RotatingFileHandler to create full log path.

        Args:
            filename: The name of the logfile.
            mode: The write mode for the file.
            maxBytes: The max file size before rotating.
            backupCount: The maximum # of backup files.
            encoding: The log file encoding.
            delay: If True, then file opening is deferred until the first call to emit().
        """
        if encoding is None and os.getenv('LANG') is None:
            encoding = 'UTF-8'
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

        # set namer
        self.namer = self.custom_gzip_namer
        self.rotator = self.custom_gzip_rotator

    @staticmethod
    def custom_gzip_namer(name):
        """Namer for rotating log handler with gz extension.

        Args:
            name: The current name of the logfile.
        """
        return name + '.gz'

    @staticmethod
    def custom_gzip_rotator(source: str, dest: str):
        """Rotate and compress log file.

        Args:
            source: The source filename.
            dest: The destination filename.
        """
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(source)
