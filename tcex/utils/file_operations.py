"""TcEx Utilities File Operations Module"""
# standard library
import gzip
import os
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional, Union


class FileOperations:
    """TcEx Utilities File Operations Class

    Args:
        out_path: The path of the defined "out" directory.
        temp_path: The path of the defined "temp" directory.
    """

    def __init__(
        self,
        out_path: Union[Optional[Path], Optional[str]] = None,
        temp_path: Union[Optional[Path], Optional[str]] = None,
    ):
        """Initialize the Class properties."""
        self.out_path = out_path or tempfile.gettempdir() or '/tmp'  # nosec
        self.temp_path = temp_path or tempfile.gettempdir() or '/tmp'  # nosec

    @staticmethod
    def _write_file(
        content: Union[bytes, str],
        fqfn: Union[Path, str],
        mode: Optional[str] = 'w',
        encoding: Optional[str] = 'utf-8',
        compress_level: Optional[int] = None,
    ) -> Path:
        """Write file content to a out directory, compressing if compress level provided.

        If passing binary data the mode needs to be set to 'wb'. If
        compress_level is provided mode is automatically set to 'wt'.

        Args:
            content: The file content.
            fqfn: A fully qualified file name.
            mode: The write mode ('w' or 'wb').
            encoding: The encoding to use when writing the file.
            compress_level: The compression level to use when writing the file.

        Returns:
            Path: Fully qualified path name for the file.
        """
        fqfn = fqfn if isinstance(fqfn, Path) else Path(fqfn)

        # ensure output directory exists
        os.makedirs(os.path.dirname(fqfn), exist_ok=True)

        # write file, either normal or compressed
        if compress_level is None:
            with open(fqfn, mode, encoding=encoding) as fh:
                fh.write(content)
        else:
            mode = 'wt'
            with gzip.open(
                fqfn,
                mode,
                compresslevel=compress_level,
                encoding=encoding,
            ) as fh:
                fh.write(content)

        # return the fully qualified path name
        return fqfn

    def _fqfn_out(self, filename: Optional[str] = None) -> str:
        """Return a unique filename for the defined "out" directory."""
        # user provided filename or generate a unique one
        filename = filename if filename is not None else str(uuid.uuid4())

        # define the fully qualified path name
        return os.path.join(self.out_path, filename)

    def _fqfn_temp(self, filename: Optional[str] = None) -> str:
        """Return a unique filename for the defined "temp" directory."""
        # user provided filename or generate a unique one
        filename = filename if filename is not None else str(uuid.uuid4())

        # define the fully qualified path name
        return os.path.join(self.temp_path, filename)

    def write_out_compressed_file(
        self,
        content: List[dict],
        filename: Optional[str] = None,
        compress_level: Optional[int] = 9,
    ) -> Path:
        """Write content to a file in the defined "out" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
            compress_level: The compression level to use when writing the file.

        Returns:
            Path: Fully qualified path name for the file.
        """
        return self._write_file(
            content, self._fqfn_out(filename), mode='wt', compress_level=compress_level
        )

    def write_out_binary_file(
        self,
        content: List[dict],
        filename: Optional[str] = None,
    ) -> Path:
        """Write content to a file in the defined "out" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.

        Returns:
            Path: Fully qualified path name for the file.
        """
        return self._write_file(content, self._fqfn_out(filename), 'wb')

    def write_temp_compressed_file(
        self,
        content: List[dict],
        filename: Optional[str] = None,
        compress_level: Optional[int] = 9,
    ) -> Path:
        """Write content to a file in the defined "temp" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
            compress_level: The compression level to use when writing the file.

        Returns:
            Path: Fully qualified path name for the file.
        """
        return self._write_file(
            content, self._fqfn_temp(filename), mode='wt', compress_level=compress_level
        )

    def write_out_file(
        self,
        content: Union[bytes, str],
        filename: Optional[str] = None,
        mode: Optional[str] = 'w',
        encoding: Optional[str] = 'utf-8',
        compress_level: Optional[int] = None,
    ) -> Path:
        """Write content to a file in the defined "out" directory.

        If passing binary data the mode needs to be set to 'wb'. If
        compress_level is provided mode is automatically set to 'wt'.

        Args:
            content: The file content.
            filename: A filename to use when writing the file.
            mode: The write mode ('w' or 'wb').
            encoding: The encoding to use when writing the file.
            compress_level: The compression level to use when writing the file.

        Returns:
            Path: Fully qualified path name for the file.
        """
        return self._write_file(content, self._fqfn_out(filename), mode, encoding, compress_level)

    def write_temp_binary_file(self, content: bytes, filename: Optional[str] = None) -> str:
        """Write content to a file in the defined "temp" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.

        Returns:
            Path: Fully qualified path name for the file.
        """
        return self._write_file(content, self._fqfn_temp(filename), 'wb')

    def write_temp_file(
        self,
        content: Union[bytes, str],
        filename: Optional[str] = None,
        mode: Optional[str] = 'w',
        encoding: Optional[str] = 'utf-8',
        compress_level: Optional[int] = None,
    ) -> str:
        """Write content to a file in the defined "temp" directory.

        If passing binary data the mode needs to be set to 'wb'.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
            mode: The write mode ('w' or 'wb').

        Returns:
            str: Fully qualified path name for the file.
        """
        return self._write_file(content, self._fqfn_temp(filename), mode, encoding, compress_level)
