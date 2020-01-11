# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""
import os


# pylint: disable=no-self-use
class TestBool:
    """Test the TcEx Utils Module."""

    def test_utils_write_temp_file(self, tcex):
        """Test writing a temp file to disk.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        filename = 'test.txt'
        fqpn = tcex.utils.write_temp_file('test', filename)
        assert os.path.isfile(fqpn)

    def test_utils_write_temp_file_no_filename(self, tcex):
        """Test writing a temp file to disk with no provided filename.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        fqpn = tcex.utils.write_temp_file('test')
        assert os.path.isfile(fqpn)

    def test_utils_write_temp_binary_file(self, tcex):
        """Test writing a binary temp file to disk.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        filename = 'test.bin'
        fqpn = tcex.utils.write_temp_binary_file(b'test', filename)
        assert os.path.isfile(fqpn)

    def test_utils_write_temp_binary_file_no_filename(self, tcex):
        """Test writing a binary temp file to disk with no provided filename.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        fqpn = tcex.utils.write_temp_binary_file(b'test')
        assert os.path.isfile(fqpn)
