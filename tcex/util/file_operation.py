"""TcEx Utilities File Operations Module"""
# standard library
import gzip
import json
import tempfile
import uuid
from pathlib import Path
from typing import Literal

COMPRESS_LEVEl = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
MODE = Literal['w', 'wb', 'wt']


class FileOperation:
    """TcEx Utilities File Operations Class

    Args:
        out_path: The path of the defined "out" directory.
        temp_path: The path of the defined "temp" directory.
    """

    def __init__(
        self,
        out_path: Path | str | None = None,
        temp_path: Path | str | None = None,
    ):
        """Initialize the Class properties."""
        self.out_path = Path(out_path or tempfile.gettempdir())
        self.temp_path = Path(temp_path or tempfile.gettempdir())

    def _fqfn_out(self, filename: Path | str | None = None) -> Path:
        """Return a unique filename for the defined "out" directory."""
        # user provided filename or generate a unique one
        filename = filename if filename is not None else str(uuid.uuid4())

        # define the fully qualified path name
        return self.out_path / filename

    def _fqfn_temp(self, filename: Path | str | None = None) -> Path:
        """Return a unique filename for the defined "temp" directory."""
        # user provided filename or generate a unique one
        filename = filename if filename is not None else str(uuid.uuid4())

        # define the fully qualified path name
        return self.temp_path / filename

    @staticmethod
    def write_file(
        content: bytes | dict | list | str,
        fqfn: Path | str,
        mode: MODE = 'w',
        encoding: str | None = None,
        compress_level: COMPRESS_LEVEl | None = None,
    ) -> Path:
        """Write file content to a out directory, compressing if compress level provided.

        If passing binary data the mode needs to be set to 'wb'. If
        compress_level is provided mode is automatically set to 'wt'.

        Args:
            content: The file content.
            fqfn: A fully qualified file name.
            mode: The write mode ('w', 'wb', 'wt').
            encoding: The encoding to use when writing the file.
            compress_level: The compression level to use when writing the file.
        """
        # encoding is not supported when writing binary data
        encoding = encoding or 'utf-8'
        if mode == 'wb':
            encoding = None

        content = json.dumps(content) if isinstance(content, (dict, list)) else content
        fqfn = fqfn if isinstance(fqfn, Path) else Path(fqfn)

        # ensure output directory exists
        fqfn.parent.mkdir(parents=True, exist_ok=True)

        # write file, either normal or compressed
        if compress_level is not None:
            # overwrite mode if compressing
            mode = 'wb' if isinstance(content, bytes) else 'wt'
            with gzip.open(
                fqfn,
                mode,
                compresslevel=compress_level,
                encoding=encoding,
            ) as fh:
                fh.write(content)  # type: ignore
        else:
            with fqfn.open(mode, encoding=encoding) as fh:
                fh.write(content)

        # return the fully qualified path name
        return fqfn

    def write_out_binary_file(
        self,
        content: bytes,
        filename: str | None = None,
    ) -> Path:
        """Write content to a file in the defined "out" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
        """
        return self.write_file(content, self._fqfn_out(filename), mode='wb')

    def write_out_compressed_file(
        self,
        content: bytes | dict | str,
        filename: Path | str | None = None,
        compress_level: COMPRESS_LEVEl = 9,
    ) -> Path:
        """Write content to a file in the defined "out" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
            compress_level: The compression level to use when writing the file.
        """
        return self.write_file(
            content, self._fqfn_out(filename), mode='wt', compress_level=compress_level
        )

    def write_out_file(
        self,
        content: bytes | dict | str,
        filename: str | None = None,
        mode: MODE = 'w',
        encoding: str = 'utf-8',
        compress_level: COMPRESS_LEVEl | None = None,
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
        """
        # TODO: [high] fix this type ignore
        encoding = encoding if mode != 'wb' else None  # type: ignore
        return self.write_file(content, self._fqfn_out(filename), mode, encoding, compress_level)

    def write_temp_binary_file(
        self,
        content: bytes,
        filename: str | None = None,
    ) -> Path:
        """Write content to a file in the defined "temp" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
        """
        return self.write_file(content, self._fqfn_temp(filename), mode='wb', encoding=None)

    def write_temp_compressed_file(
        self,
        content: bytes | dict | str,
        filename: str | None = None,
        compress_level: COMPRESS_LEVEl = 9,
    ) -> Path:
        """Write content to a file in the defined "temp" directory.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
            compress_level: The compression level to use when writing the file.
        """
        return self.write_file(
            content, self._fqfn_temp(filename), mode='wt', compress_level=compress_level
        )

    def write_temp_file(
        self,
        content: bytes | dict | str,
        filename: Path | str | None = None,
        mode: MODE = 'w',
        encoding: str = 'utf-8',
        compress_level: COMPRESS_LEVEl | None = None,
    ) -> Path:
        """Write content to a file in the defined "temp" directory.

        If passing binary data the mode needs to be set to 'wb'.

        Args:
            content: The file content.
            filename: The filename to use when writing the file.
            mode: The write mode ('w' or 'wb').
            encoding: The encoding to use when writing the file.
            compress_level: The compression level to use when writing the file.
        """
        # TODO: [high] fix this type ignore
        encoding = encoding if mode != 'wb' else None  # type: ignore
        return self.write_file(content, self._fqfn_temp(filename), mode, encoding, compress_level)
