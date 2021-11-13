"""TcEx Utilities File Operations Module"""
# standard library
import os
import tempfile
import uuid
from typing import Optional, Union


class FileOperations:
    """TcEx Utilities File Operations Class

    Args:
        temp_path: The path to write temp files.
    """

    def __init__(self, temp_path: Optional[str] = None):
        """Initialize the Class properties."""
        self.temp_path = temp_path or tempfile.gettempdir() or '/tmp'  # nosec

    def write_temp_binary_file(self, content: bytes, filename: Optional[str] = None) -> str:
        """Write content to a temporary file.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.

        Returns:
            str: Fully qualified path name for the file.
        """
        return self.write_temp_file(content, filename, 'wb')

    def write_temp_file(
        self, content: Union[bytes, str], filename: Optional[str] = None, mode: Optional[str] = 'w'
    ) -> str:
        """Write content to a temporary file.

        If passing binary data the mode needs to be set to 'wb'.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
            mode: The write mode ('w' or 'wb').

        Returns:
            str: Fully qualified path name for the file.
        """
        if filename is None:
            filename = str(uuid.uuid4())
        fqpn = os.path.join(self.temp_path, filename)
        os.makedirs(os.path.dirname(fqpn), exist_ok=True)
        with open(fqpn, mode) as fh:
            fh.write(content)
        return fqpn
