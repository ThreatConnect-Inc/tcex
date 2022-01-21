"""Test the TcEx Utils Module."""
# standard library
import os
from typing import TYPE_CHECKING

# first-party
from tcex.utils.file_operations import FileOperations

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


# pylint: disable=no-self-use
class TestBool:
    """Test the TcEx Utils Module."""

    def test_utils_write_temp_file(self, tcex: 'TcEx'):
        """Test writing a temp file to disk.

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        file_operations = FileOperations(tcex.inputs.model.tc_temp_path)
        filename = 'test.txt'
        fqpn = file_operations.write_temp_file('test', filename)
        assert os.path.isfile(fqpn)

    def test_utils_write_temp_file_no_filename(self, tcex: 'TcEx'):
        """Test writing a temp file to disk with no provided filename.

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        file_operations = FileOperations(tcex.inputs.model.tc_temp_path)
        fqpn = file_operations.write_temp_file('test')
        assert os.path.isfile(fqpn)

    def test_utils_write_temp_binary_file(self, tcex: 'TcEx'):
        """Test writing a binary temp file to disk.

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        file_operations = FileOperations(tcex.inputs.model.tc_temp_path)
        filename = 'test.bin'
        fqpn = file_operations.write_temp_binary_file(b'test', filename)
        assert os.path.isfile(fqpn)

    def test_utils_write_temp_binary_file_no_filename(self, tcex: 'TcEx'):
        """Test writing a binary temp file to disk with no provided filename.

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        file_operations = FileOperations(tcex.inputs.model.tc_temp_path)
        fqpn = file_operations.write_temp_binary_file(b'test')
        assert os.path.isfile(fqpn)
