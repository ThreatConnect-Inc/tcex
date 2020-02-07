# -*- coding: utf-8 -*-
"""Test the TcEx output Decorator."""
import pytest
from tcex import Output


# pylint: disable=no-self-use
class TestOutputDecorators:
    """Test the TcEx ReadArg Decorators."""

    args = None
    output_data = None
    output_data_list = None
    tcex = None

    def setup_method(self):
        """Perform after test cleanup."""
        self.output_data = None
        self.output_data_list = []

    @Output(attribute='output_data', overwrite=False)
    def output(self, data):
        """Test output decorator."""
        return data

    @pytest.mark.parametrize(
        'value', [(None), ('one'), ([None]), (''), ([''])],
    )
    def test_output(self, value):
        """Test Output decorator."""
        self.output(value)
        assert self.output_data == value

    @pytest.mark.parametrize(
        'value1,value2,expected',
        [
            (None, None, [None, None]),
            (None, [None], [None, None]),
            ([None], [None], [None, None]),
            ('', '', ['', '']),
            ([''], '', ['', '']),
            ('one', 'one', ['one', 'one']),
            ('one', ['one'], ['one', 'one']),
        ],
    )
    def test_output_multiple(self, value1, value2, expected):
        """Test Output decorator."""
        self.output(value1)
        self.output(value2)
        assert self.output_data == expected

    @Output(attribute='output_data', overwrite=True)
    def output_overwrite_true(self, data):
        """Test output decorator."""
        return data

    @pytest.mark.parametrize(
        'value1,value2',
        [
            (None, 'test'),
            ('test', None),
            ([None], [None, None]),
            ('', ['', '']),
            ([''], ['', '']),
            ('one', ['one', 'one']),
        ],
    )
    def test_output_overwrite_true(self, value1, value2):
        """Test Output decorator."""
        self.output_overwrite_true(value1)
        self.output_overwrite_true(value2)
        assert self.output_data == value2

    @Output(attribute='output_data_list', overwrite=False)
    def output_list(self, data):
        """Test output decorator."""
        return data

    @pytest.mark.parametrize(
        'value,expected',
        [(None, [None]), ([None], [None]), ('', ['']), ([''], ['']), ('one', ['one'])],
    )
    def test_output_list(self, value, expected):
        """Test Output decorator."""
        self.output_list(value)
        assert self.output_data_list == expected
