"""Test the TcEx Utils Module."""
# standard library
import gzip
import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


# pylint: disable=no-self-use
class TestFileOperations:
    """Test the TcEx Utils Module."""

    def test_fqfn_out(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.file_operations._fqfn_out(filename)
        assert str(fqfn).endswith(filename)  # nosec

    def test_fqfn_temp(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.file_operations._fqfn_temp(filename)
        assert str(fqfn).endswith(filename)  # nosec

    def test_write_file(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.file_operations.write_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_file_dict(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        contents = {'name': request.node.name}
        filename = os.path.join('data', f'{request.node.name}.txt')
        fqfn = tcex.file_operations.write_file(contents, filename)
        assert fqfn.is_file()  # nosec
        assert json.loads(fqfn.read_text()) == contents  # nosec

    def test_write_file_nested(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = os.path.join('data', f'{request.node.name}.txt')
        fqfn = tcex.file_operations.write_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_out_binary_file(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.bin'
        fqfn = tcex.file_operations.write_out_binary_file(request.node.name.encode(), filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_bytes() == request.node.name.encode()  # nosec

    def test_write_out_compressed_file(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.gz'
        fqfn = tcex.file_operations.write_out_compressed_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        with gzip.open(fqfn, 'rt') as fh:
            assert fh.read() == request.node.name  # nosec

    def test_write_out_file(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.file_operations.write_out_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_temp_binary_file(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.bin'
        fqfn = tcex.file_operations.write_temp_binary_file(request.node.name.encode(), filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_bytes() == request.node.name.encode()  # nosec

    def test_write_temp_compressed_file(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.gz'
        fqfn = tcex.file_operations.write_temp_compressed_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        with gzip.open(fqfn, 'rt') as fh:
            assert fh.read() == request.node.name  # nosec

    def test_write_temp_file(self, request: ..., tcex: 'TcEx'):
        """Test Case

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
            request (fixture): The pytest request object.
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.file_operations.write_temp_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec
