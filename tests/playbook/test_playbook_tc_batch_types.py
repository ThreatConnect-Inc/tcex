"""Test the TcEx Batch Module."""
# standard library
import json
import os
from typing import TYPE_CHECKING, Any

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex.playbook.playbook import Playbook


class TestUtils:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,filename',
        [
            ('#App:0002:tb1!TCBatch', 'large_file'),
            ('#App:0002:tb2!TCBatch', 'empty_indicators'),
            ('#App:0002:tb3!TCBatch', 'empty_groups'),
            ('#App:0002:tb4!TCBatch', 'small_file'),
        ],
    )
    def test_playbook_tc_batch_pass(
        self, variable: str, filename: str, playbook: 'Playbook', request: 'pytest.FixtureRequest'
    ):
        """Test playbook variables."""
        abspath = os.path.join(request.fspath.dirname, 'batch_test_input', f'{filename}.json')

        with open(abspath) as file:
            data = json.load(file)
        playbook.create.tc_batch(variable, data, when_requested=False)
        result = playbook.read.tc_batch(variable)
        assert result == data, f'result of ({result}) does not match ({data})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!TCBatch', []),
            ('#App:0002:b2!TCBatch', {'indicator': {}, 'group': {}}),
            ('#App:0002:b3!TCBatch', {'indicator': [], 'group': 'invalid group'}),
            ('#App:0002:b4!TCBatch', {'indicator': 'invalid indicator', 'group': []}),
            ('#App:0002:b5!TCBatch', {'indicator': None, 'group': [{'one': '1', 'two': 'two'}]}),
            ('#App:0002:b6!TCBatch', {'indicator': [{'one': '1', 'two': 'two'}], 'group': None}),
            ('#App:0002:b7!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_tc_batch_fail(self, variable: str, value: Any, playbook: 'Playbook'):
        """Test playbook variables."""
        try:
            playbook.create.tc_batch(variable, value, when_requested=False)
            assert False, f'{value} is not a valid TCBatch value'
        except RuntimeError:
            assert True
