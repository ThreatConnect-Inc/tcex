"""TestFileOperation for file operations and manipulations.

Test suite for the file operation utility methods that handle various file operations
including writing, reading, compression, and temporary file management.

Classes:
    TestFileOperation: Test suite for file operations

TcEx Module Tested: tcex.app.file_operation
"""


import gzip
import json
from pathlib import Path


from _pytest.fixtures import FixtureRequest


from tcex import TcEx


class TestFileOperation:
    """TestFileOperation for file operations and manipulations.

    Test suite for the file operation utility methods that handle various file
    operations including writing, reading, compression, and temporary file
    management.
    """

    def test_fqfn_out(self, request: FixtureRequest, tcex: TcEx):
        """Test fully qualified filename output path generation.

        Test case for generating fully qualified filenames for output files
        using the _fqfn_out method.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation._fqfn_out(filename)
        assert str(fqfn).endswith(filename)  # nosec

    def test_fqfn_temp(self, request: FixtureRequest, tcex: TcEx):
        """Test fully qualified filename temporary path generation.

        Test case for generating fully qualified filenames for temporary files
        using the _fqfn_temp method.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation._fqfn_temp(filename)
        assert str(fqfn).endswith(filename)  # nosec

    def test_write_file(self, request: FixtureRequest, tcex: TcEx):
        """Test basic file writing functionality.

        Test case for writing string content to a file using the write_file
        method and verifying the file was created with correct content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_file_dict(self, request: FixtureRequest, tcex: TcEx):
        """Test dictionary content file writing functionality.

        Test case for writing dictionary content to a JSON file using the
        write_file method and verifying the file was created with correct
        JSON content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        contents = {'name': request.node.name}
        filename = Path('data') / f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_file(contents, filename)
        assert fqfn.is_file()  # nosec
        assert json.loads(fqfn.read_text()) == contents  # nosec

    def test_write_file_nested(self, request: FixtureRequest, tcex: TcEx):
        """Test nested directory file writing functionality.

        Test case for writing string content to a file in a nested directory
        using the write_file method and verifying the file was created with
        correct content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = Path('data') / f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_out_binary_file(self, request: FixtureRequest, tcex: TcEx):
        """Test binary file writing functionality.

        Test case for writing binary content to an output file using the
        write_out_binary_file method and verifying the file was created with
        correct binary content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.bin'
        fqfn = tcex.app.file_operation.write_out_binary_file(request.node.name.encode(), filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_bytes() == request.node.name.encode()  # nosec

    def test_write_out_compressed_file(self, request: FixtureRequest, tcex: TcEx):
        """Test compressed file writing functionality.

        Test case for writing compressed content to an output file using the
        write_out_compressed_file method and verifying the file was created
        with correct compressed content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.gz'
        fqfn = tcex.app.file_operation.write_out_compressed_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        with gzip.open(fqfn, 'rt') as fh:
            assert fh.read() == request.node.name  # nosec

    def test_write_out_file(self, request: FixtureRequest, tcex: TcEx):
        """Test output file writing functionality.

        Test case for writing string content to an output file using the
        write_out_file method and verifying the file was created with
        correct content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_out_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec

    def test_write_temp_binary_file(self, request: FixtureRequest, tcex: TcEx):
        """Test temporary binary file writing functionality.

        Test case for writing binary content to a temporary file using the
        write_temp_binary_file method and verifying the file was created with
        correct binary content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.bin'
        fqfn = tcex.app.file_operation.write_temp_binary_file(request.node.name.encode(), filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_bytes() == request.node.name.encode()  # nosec

    def test_write_temp_compressed_file(self, request: FixtureRequest, tcex: TcEx):
        """Test temporary compressed file writing functionality.

        Test case for writing compressed content to a temporary file using the
        write_temp_compressed_file method and verifying the file was created
        with correct compressed content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.gz'
        fqfn = tcex.app.file_operation.write_temp_compressed_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        with gzip.open(fqfn, 'rt') as fh:
            assert fh.read() == request.node.name  # nosec

    def test_write_temp_file(self, request: FixtureRequest, tcex: TcEx):
        """Test temporary file writing functionality.

        Test case for writing string content to a temporary file using the
        write_temp_file method and verifying the file was created with
        correct content.

        Fixtures:
            request: Pytest fixture request object for test metadata
            tcex: TcEx application instance for testing
        """
        filename = f'{request.node.name}.txt'
        fqfn = tcex.app.file_operation.write_temp_file(request.node.name, filename)
        assert fqfn.is_file()  # nosec
        assert fqfn.read_text() == request.node.name  # nosec
