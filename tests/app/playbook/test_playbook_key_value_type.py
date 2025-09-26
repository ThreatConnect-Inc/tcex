"""TestPlaybookKeyValueType for TcEx App Playbook Key Value Type Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Key Value Type Module,
specifically testing key-value and key-value array variable functionality including creation,
reading, validation, deletion, and error handling across various data types and formats
for playbook variable operations.

Classes:
    TestPlaybookKeyValueType: Test class for TcEx App Playbook Key Value Type Module functionality

TcEx Module Tested: app.playbook.playbook
"""


from typing import Any


import pytest


from tcex.app.playbook.playbook import Playbook  # TYPE-CHECKING
from tcex.input.field_type import KeyValue


class TestPlaybookKeyValueType:
    """TestPlaybookKeyValueType for TcEx App Playbook Key Value Type Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Key Value Type Module,
    covering various key-value and key-value array scenarios including successful operations,
    failure handling, type validation, and proper cleanup across different playbook
    variable types and data formats.
    """

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0002:kv1!KeyValue', {'key': 'one', 'value': '1'}, id='pass-keyvalue-1'
            ),
            pytest.param(
                '#App:0002:kv2!KeyValue', {'key': 'two', 'value': '2'}, id='pass-keyvalue-2'
            ),
            pytest.param(
                '#App:0002:kv3!KeyValue', {'key': 'three', 'value': '3'}, id='pass-keyvalue-3'
            ),
            pytest.param(
                '#App:0002:kv4!KeyValue', {'key': 'four', 'value': '4'}, id='pass-keyvalue-4'
            ),
            pytest.param(
                '#App:0002:kv5!KeyValue',
                KeyValue(key='five', value='5'),  # type: ignore
                id='pass-keyvalue-5',
            ),
        ],
    )
    def test_playbook_key_value_pass(
        self, variable: str, value: dict | KeyValue, playbook: Playbook
    ) -> None:
        """Test Playbook Key Value Pass for TcEx App Playbook Key Value Type Module.

        This test case verifies that key-value variables can be successfully created,
        read, and deleted in the playbook system, ensuring proper key-value data
        handling and storage operations including both dict and KeyValue object types.

        Parameters:
            variable: The playbook variable name to test
            value: The key-value data to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing key-value operations
        """
        playbook.create.key_value(variable, value, when_requested=False)
        result = playbook.read.key_value(variable)
        if isinstance(value, KeyValue):
            value = value.model_dump(exclude_unset=True)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0002:b1!KeyValue',
                {'one': '1', 'two': 'two'},
                id='fail-invalid-keyvalue-structure',
            ),
            pytest.param('#App:0002:b2!KeyValue', [], id='fail-list-type'),
            pytest.param('#App:0002:b3!KeyValue', {}, id='fail-empty-dict'),
            pytest.param('#App:0002:b4!WrongType', 'wrong type', id='fail-wrong-type'),
        ],
    )
    def test_playbook_key_value_fail(self, variable: str, value: Any, playbook: Playbook) -> None:
        """Test Playbook Key Value Fail for TcEx App Playbook Key Value Type Module.

        This test case verifies that key-value variables properly reject invalid data
        types by testing various non-key-value inputs and ensuring appropriate
        RuntimeError exceptions are raised for invalid data structures.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing key-value operations
        """
        try:
            playbook.create.key_value(variable, value, when_requested=False)
            pytest.fail(f'{value} is not a valid Key Value type')
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0003:kv1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                id='pass-keyvalue-array-1',
            ),
            pytest.param(
                '#App:0003:kv2!KeyValueArray',
                [{'key': 'three', 'value': '3'}, {'key': 'four', 'value': '4'}],
                id='pass-keyvalue-array-2',
            ),
            pytest.param(
                '#App:0003:kv3!KeyValueArray',
                [{'key': 'five', 'value': '5'}, {'key': 'six', 'value': '6'}],
                id='pass-keyvalue-array-3',
            ),
            pytest.param(
                '#App:0003:kv4!KeyValueArray',
                [{'key': 'seven', 'value': '7'}, {'key': 'eight', 'value': '8'}],
                id='pass-keyvalue-array-4',
            ),
        ],
    )
    def test_playbook_key_value_array_pass(
        self, variable: str, value: list[dict[str, str]], playbook: Playbook
    ) -> None:
        """Test Playbook Key Value Array Pass for TcEx App Playbook Key Value Type Module.

        This test case verifies that key-value array variables can be successfully
        created, read, and deleted in the playbook system, ensuring proper
        key-value array data handling and storage operations.

        Parameters:
            variable: The playbook variable name to test
            value: The key-value array data to store and retrieve

        Fixtures:
            playbook: Playbook instance for testing key-value array operations
        """
        playbook.create.key_value_array(variable, value, when_requested=False)  # type: ignore
        result = playbook.read.key_value_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0003:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'k': 'two', 'v': '2'}],
                id='fail-invalid-keyvalue-array-structure',
            ),
            pytest.param(
                '#App:0003:kva1!KeyValueArray', 'not a KeyValueArray', id='fail-string-type'
            ),
            pytest.param('#App:0002:b3!WrongType', 'wrong type', id='fail-wrong-variable-type'),
        ],
    )
    def test_playbook_key_value_array_fail(
        self, variable: str, value: Any, playbook: Playbook
    ) -> None:
        """Test Playbook Key Value Array Fail for TcEx App Playbook Key Value Type Module.

        This test case verifies that key-value array variables properly reject invalid
        data types by testing various non-key-value-array inputs and ensuring
        appropriate RuntimeError exceptions are raised for invalid data structures.

        Parameters:
            variable: The playbook variable name to test
            value: The invalid data value that should cause failure

        Fixtures:
            playbook: Playbook instance for testing key-value array operations
        """
        try:
            playbook.create.key_value_array(variable, value, when_requested=False)
            pytest.fail(f'{value} is not a valid Key Value Array value')
        except RuntimeError:
            assert True
