# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest


# pylint: disable=no-self-use
class TestUtils:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:kv1!KeyValue', {'key': 'one', 'value': '1'}),
            ('#App:0002:kv2!KeyValue', {'key': 'two', 'value': '2'}),
            ('#App:0002:kv3!KeyValue', {'key': 'three', 'value': '3'}),
            ('#App:0002:kv4!KeyValue', {'key': 'four', 'value': '4'}),
        ],
    )
    def test_playbook_key_value(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_key_value(variable, value)
        result = tcex.playbook.read_key_value(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!KeyValue', {'one': '1', 'two': 'two'}),
            ('#App:0002:b2!KeyValue', []),
            ('#App:0002:b3!KeyValue', {}),
            ('#App:0002:b4!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_key_value_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_key_value(variable, value)
            assert False, f'{value} is not a valid Binary value'
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            (
                '#App:0003:kv1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
            ),
            (
                '#App:0003:kv2!KeyValueArray',
                [{'key': 'three', 'value': '3'}, {'key': 'four', 'value': '4'}],
            ),
            (
                '#App:0003:kv3!KeyValueArray',
                [{'key': 'five', 'value': '5'}, {'key': 'six', 'value': '6'}],
            ),
            (
                '#App:0003:kv4!KeyValueArray',
                [{'key': 'seven', 'value': '7'}, {'key': 'eight', 'value': '8'}],
            ),
        ],
    )
    def test_playbook_key_value_array(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_key_value_array(variable, value)
        result = tcex.playbook.read_key_value_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            (
                '#App:0003:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'k': 'two', 'v': '2'}],
            ),
            ('#App:0003:kva1!KeyValueArray', 'not a KeyValueArray'),
            ('#App:0002:b3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_key_value_array_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_key_value_array(variable, value)
            assert False, f'{value} is not a valid Binary Array value'
        except RuntimeError:
            assert True
