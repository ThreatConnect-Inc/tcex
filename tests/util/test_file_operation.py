"""TcEx Framework Module"""
# standard library
import gzip
import json
import os

# third-party
from _pytest.fixtures import FixtureRequest

# first-party
from tcex import TcEx


class TestFileOperation:
    """Test Suite"""

    def test_fqfn_out(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation._fqfn_out(filename)
        assert str(fqfn).endswith(filename)  # nosec

    def test_fqfn_temp(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation._fqfn_temp(filename)
        assert str(fqfn).endswith(filename)  # nosec

    def test_write_file(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_file_dict(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        contents = {'name': request.node.name}
        filename = os.path.join('data', f'{request.node.name}.txt')
        fqfn = tcex.app.file_operation.write_file(contents, filename)
        assert fqfn.is_file()  # nosec
        assert json.loads(fqfn.read_text()) == contents  # nosec

    def test_write_file_nested(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = os.path.join('data', f'{request.node.name}.txt')
        fqfn = tcex.app.file_operation.write_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_out_binary_file(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.bin'
        fqfn = tcex.app.file_operation.write_out_binary_file(request.node.name.encode(), filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_bytes() == request.node.name.encode()  # nosec

    def test_write_out_compressed_file(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.gz'
        fqfn = tcex.app.file_operation.write_out_compressed_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        with gzip.open(fqfn, 'rt') as fh:
            assert fh.read() == request.node.name  # nosec

    def test_write_out_file(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_out_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_temp_binary_file(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.bin'
        fqfn = tcex.app.file_operation.write_temp_binary_file(request.node.name.encode(), filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_bytes() == request.node.name.encode()  # nosec

    def test_write_temp_compressed_file(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.gz'
        fqfn = tcex.app.file_operation.write_temp_compressed_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        with gzip.open(fqfn, 'rt') as fh:
            assert fh.read() == request.node.name  # nosec

    def test_write_temp_file(self, request: FixtureRequest, tcex: TcEx):
        """Test Case."""
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_temp_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec
