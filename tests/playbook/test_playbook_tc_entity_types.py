"""Test the TcEx Batch Module."""
# standard library
from typing import TYPE_CHECKING, Any, Dict, List, Union

# third-party
import pytest

# first-party
from tcex.input.field_models import KeyValue

if TYPE_CHECKING:
    # first-party
    from tcex.playbook.playbook import Playbook


# pylint: disable=no-self-use
class TestUtils:
    """Test the TcEx Batch Module."""

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:te1!TCEntity', {'id': '001', 'value': '1.1.1.1', 'type': 'Address'}),
            ('#App:0002:te2!TCEntity', {'id': '002', 'value': '2.2.2.2', 'type': 'Address'}),
            ('#App:0002:te3!TCEntity', {'id': '003', 'value': '3.3.3.3', 'type': 'Address'}),
            ('#App:0002:te4!TCEntity', {'id': '004', 'value': '3.3.3.3', 'type': 'Address'}),
        ],
    )
    def test_playbook_tc_entity_pass(
        self, variable: str, value: Union[dict, KeyValue], playbook: 'Playbook'
    ):
        """Test playbook variables."""
        playbook.create.tc_entity(variable, value, when_requested=False)
        result = playbook.read.tc_entity(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!TCEntity', {'one': '1', 'two': 'two'}),
            ('#App:0002:b2!TCEntity', []),
            ('#App:0002:b3!TCEntity', {}),
            ('#App:0002:b4!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_tc_entity_fail(self, variable: str, value: Any, playbook: 'Playbook'):
        """Test playbook variables."""
        try:
            playbook.create.tc_entity(variable, value, when_requested=False)
            assert False, f'{value} is not a valid TCEntity value'
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'variable,value',
        [
            (
                '#App:0002:tea1!TCEntityArray',
                [
                    {'id': '001', 'value': '1.1.1.1', 'type': 'Address'},
                    {'id': '011', 'value': '11.11.11.11', 'type': 'Address'},
                ],
            ),
            (
                '#App:0002:tea2!TCEntityArray',
                [
                    {'id': '002', 'value': '2.2.2.2', 'type': 'Address'},
                    {'id': '022', 'value': '22.22.22.22', 'type': 'Address'},
                ],
            ),
            (
                '#App:0002:tea3!TCEntityArray',
                [
                    {'id': '003', 'value': '3.3.3.3', 'type': 'Address'},
                    {'id': '033', 'value': '33.33.33.33', 'type': 'Address'},
                ],
            ),
            (
                '#App:0002:tea4!TCEntityArray',
                [
                    {'id': '004', 'value': '4.4.4.4', 'type': 'Address'},
                    {'id': '044', 'value': '44.44.44.44', 'type': 'Address'},
                ],
            ),
        ],
    )
    def test_playbook_tc_entity_array_pass(
        self, variable: str, value: List[Dict[str, str]], playbook: 'Playbook'
    ):
        """Test playbook variables."""
        playbook.create.tc_entity_array(variable, value, when_requested=False)
        result = playbook.read.tc_entity_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            (
                '#App:0003:tea1!TCEntityArray',
                [
                    {'id': '001', 'value': '1.1.1.1', 'type': 'Address'},
                    {'id': '011', 'ip': '11.11.11.11', 'type': 'Address'},
                ],
            ),
            ('#App:0003:tea2!TCEntityArray', 'not a TCEntityArray'),
            ('#App:0003:tea3!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_tc_entity_array_fail(self, variable: str, value: Any, playbook: 'Playbook'):
        """Test playbook variables."""
        with pytest.raises(RuntimeError) as ex:
            playbook.create.tc_entity_array(variable, value, when_requested=False)

        assert 'Invalid ' in str(ex.value)
