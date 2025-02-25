"""TcEx Framework Module"""

# standard library
import gzip
import os
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path


class RotatingFileHandlerCustom(RotatingFileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(
        self,
        filename: str,
        mode: str = 'a',
        maxBytes: int = 0,  # noqa: N803
        backupCount: int = 0,  # noqa: N803
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

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
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
        source_filename = Path(source)
        with source_filename.open(mode='rb') as f_in, gzip.open(dest, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        source_filename.unlink()
