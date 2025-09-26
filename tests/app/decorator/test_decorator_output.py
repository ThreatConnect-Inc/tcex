"""TestDecoratorOutput for TcEx App Decorator Output Module Testing.

This module contains comprehensive test cases for the TcEx App Decorator Output Module,
specifically testing the Output decorator functionality including attribute storage,
data writing, appending, extending, and proper decorator behavior across different
output scenarios for storing method return values in App attributes.

Classes:
    TestDecoratorOutput: Test class for TcEx App Decorator Output Module functionality

TcEx Module Tested: app.decorator.output
"""


from typing import Any

import pytest


from tcex.app.decorator.output import Output


class TestDecoratorOutput:
    """TestDecoratorOutput for TcEx App Decorator Output Module Testing.

    This class provides comprehensive testing for the TcEx App Decorator Output Module,
    covering various output decorator scenarios including attribute storage, data
    writing, appending, extending, and proper decorator behavior for storing
    method return values in App attributes.
    """

    args: Any = None
    output_data: Any = None
    output_data_list: list[Any] | None = None
    tcex: Any = None

    def setup_method(self) -> None:
        """Perform after test cleanup.

        This method is called before each test method to reset the output
        data attributes to their initial state for clean testing.
        """
        self.output_data = None
        self.output_data_list = []

    @Output(attribute='output_data', overwrite=False)  # type: ignore
    def output(self, data: Any) -> Any:
        """Test output decorator with overwrite disabled.

        This method is decorated with the Output decorator to test its functionality
        for storing return values in App attributes without overwriting.
        """
        return data

    @pytest.mark.parametrize(
        'value',
        [
            pytest.param(None, id='pass-none-value'),
            pytest.param('one', id='pass-string-value'),
            pytest.param([None], id='pass-none-list'),
            pytest.param('', id='pass-empty-string'),
            pytest.param([''], id='pass-empty-string-list'),
        ],
    )
    def test_output(self, value: Any) -> None:
        """Test Output Decorator for TcEx App Decorator Output Module.

        This test case verifies that the Output decorator properly stores
        return values in App attributes when overwrite is disabled,
        ensuring the decorator correctly handles various data types
        including None, strings, and lists.

        Parameters:
            value: The data value to test with the output decorator
        """
        self.output(value)
        assert self.output_data == value, (
            f'output data ({self.output_data}) does not match expected ({value})'
        )

    @pytest.mark.parametrize(
        'value1,value2,expected',
        [
            pytest.param(None, None, [None, None], id='pass-none-none'),
            pytest.param(None, [None], [None, None], id='pass-none-none-list'),
            pytest.param([None], [None], [None, None], id='pass-none-list-none-list'),
            pytest.param('', '', ['', ''], id='pass-empty-empty'),
            pytest.param([''], '', ['', ''], id='pass-empty-list-empty'),
            pytest.param('one', 'one', ['one', 'one'], id='pass-string-string'),
            pytest.param('one', ['one'], ['one', 'one'], id='pass-string-string-list'),
        ],
    )
    def test_output_multiple(self, value1: Any, value2: Any, expected: list[Any]) -> None:
        """Test Output Decorator Multiple Calls for TcEx App Decorator Output Module.

        This test case verifies that the Output decorator properly handles
        multiple calls when overwrite is disabled, ensuring the decorator
        correctly appends or extends data based on the existing attribute
        type and new data structure.

        Parameters:
            value1: The first data value to test
            value2: The second data value to test
            expected: The expected result after both calls
        """
        self.output(value1)
        self.output(value2)
        assert self.output_data == expected, (
            f'output data ({self.output_data}) does not match expected ({expected})'
        )

    @Output(attribute='output_data', overwrite=True)  # type: ignore
    def output_overwrite_true(self, data: Any) -> Any:
        """Test output decorator with overwrite enabled.

        This method is decorated with the Output decorator to test its functionality
        for storing return values in App attributes with overwriting enabled.
        """
        return data

    @pytest.mark.parametrize(
        'value1,value2',
        [
            pytest.param(None, 'test', id='pass-none-test'),
            pytest.param('test', None, id='pass-test-none'),
            pytest.param([None], [None, None], id='pass-none-list-extended'),
            pytest.param('', ['', ''], id='pass-empty-string-list'),
            pytest.param([''], ['', ''], id='pass-empty-list-string-list'),
            pytest.param('one', ['one', 'one'], id='pass-string-string-list'),
        ],
    )
    def test_output_overwrite_true(self, value1: Any, value2: Any) -> None:
        """Test Output Decorator Overwrite Enabled for TcEx App Decorator Output Module.

        This test case verifies that the Output decorator properly overwrites
        existing attribute values when overwrite is enabled, ensuring the
        decorator correctly replaces previous data with new return values.

        Parameters:
            value1: The first data value to test
            value2: The second data value that should overwrite the first
        """
        self.output_overwrite_true(value1)
        self.output_overwrite_true(value2)
        assert self.output_data == value2, (
            f'output data ({self.output_data}) does not match expected ({value2})'
        )

    @Output(attribute='output_data_list', overwrite=False)  # type: ignore
    def output_list(self, data: Any) -> Any:
        """Test output decorator with list attribute.

        This method is decorated with the Output decorator to test its functionality
        for storing return values in list-type App attributes.
        """
        return data

    @pytest.mark.parametrize(
        'value,expected',
        [
            pytest.param(None, [None], id='pass-none-to-list'),
            pytest.param([None], [None], id='pass-none-list-to-list'),
            pytest.param('', [''], id='pass-empty-string-to-list'),
            pytest.param([''], [''], id='pass-empty-list-to-list'),
            pytest.param('one', ['one'], id='pass-string-to-list'),
        ],
    )
    def test_output_list(self, value: Any, expected: list[Any]) -> None:
        """Test Output Decorator List Attribute for TcEx App Decorator Output Module.

        This test case verifies that the Output decorator properly handles
        list-type attributes, ensuring the decorator correctly converts
        single values to lists and handles existing list data appropriately.

        Parameters:
            value: The data value to test with the list output decorator
            expected: The expected result in the list attribute
        """
        self.output_list(value)
        assert self.output_data_list == expected, (
            f'output data list ({self.output_data_list}) does not match expected ({expected})'
        )
