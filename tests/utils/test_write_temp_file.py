# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import os
from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestBool:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""

    @staticmethod
    def test_write_temp_file():
        """Test any to datetime"""
        filename = 'test.txt'
        fqpn = tcex.utils.write_temp_file('test', filename)
        assert os.path.isfile(fqpn)

    @staticmethod
    def test_write_temp_file_no_filename():
        """Test any to datetime"""
        fqpn = tcex.utils.write_temp_file('test')
        assert os.path.isfile(fqpn)

    @staticmethod
    def test_write_temp_binary_file():
        """Test any to datetime"""
        filename = 'test.bin'
        fqpn = tcex.utils.write_temp_binary_file(b'test', filename)
        assert os.path.isfile(fqpn)

    @staticmethod
    def test_write_temp_binary_file_no_filename():
        """Test any to datetime"""
        fqpn = tcex.utils.write_temp_binary_file(b'test')
        assert os.path.isfile(fqpn)
