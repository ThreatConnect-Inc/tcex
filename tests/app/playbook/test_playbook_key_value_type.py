"""TcEx Framework Module"""

# standard library
from typing import Any

# third-party
import pytest

# first-party
from tcex.app.playbook.playbook import Playbook  # TYPE-CHECKING
from tcex.input.field_type import KeyValue


class TestUtils:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:kv1!KeyValue', {'key': 'one', 'value': '1'}),
            ('#App:0002:kv2!KeyValue', {'key': 'two', 'value': '2'}),
            ('#App:0002:kv3!KeyValue', {'key': 'three', 'value': '3'}),
            ('#App:0002:kv4!KeyValue', {'key': 'four', 'value': '4'}),
            ('#App:0002:kv5!KeyValue', KeyValue(**{'key': 'five', 'value': '5'})),  # type: ignore
        ],
    )
    def test_playbook_key_value_pass(
        self, variable: str, value: dict | KeyValue, playbook: Playbook
    ):
        """Test playbook variables."""
        playbook.create.key_value(variable, value, when_requested=False)
        result = playbook.read.key_value(variable)
        if isinstance(value, KeyValue):
            value = value.dict(exclude_unset=True)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!KeyValue', {'one': '1', 'two': 'two'}),
            ('#App:0002:b2!KeyValue', []),
            ('#App:0002:b3!KeyValue', {}),
            ('#App:0002:b4!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_key_value_fail(self, variable: str, value: Any, playbook: Playbook):
        """Test playbook variables."""
        try:
            playbook.create.key_value(variable, value, when_requested=False)
            assert False, f'{value} is not a valid Key Value type'
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
    def test_playbook_key_value_array_pass(
        self, variable: str, value: list[dict[str, str]], playbook: Playbook
    ):
        """Test playbook variables."""
        playbook.create.key_value_array(variable, value, when_requested=False)  # type: ignore
        result = playbook.read.key_value_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

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
    def test_playbook_key_value_array_fail(self, variable: str, value: Any, playbook: Playbook):
        """Test playbook variables."""
        try:
            playbook.create.key_value_array(variable, value, when_requested=False)
            assert False, f'{value} is not a valid Key Value Array value'
        except RuntimeError:
            assert True
