# -*- coding: utf-8 -*-
"""Test the TcEx Utils Module."""
import os
from ..tcex_init import tcex


class TestBool:
    """Test the TcEx Utils Module."""

    @staticmethod
    def test_utils_write_temp_file():
        """Test any to datetime"""
        filename = 'test.txt'
        fqpn = tcex.utils.write_temp_file('test', filename)
        assert os.path.isfile(fqpn)

    @staticmethod
    def test_utils_write_temp_file_no_filename():
        """Test any to datetime"""
        fqpn = tcex.utils.write_temp_file('test')
        assert os.path.isfile(fqpn)

    @staticmethod
    def test_utils_write_temp_binary_file():
        """Test any to datetime"""
        filename = 'test.bin'
        fqpn = tcex.utils.write_temp_binary_file(b'test', filename)
        assert os.path.isfile(fqpn)

    @staticmethod
    def test_utils_write_temp_binary_file_no_filename():
        """Test any to datetime"""
        fqpn = tcex.utils.write_temp_binary_file(b'test')
        assert os.path.isfile(fqpn)
