# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
# third-party
import pytest


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
    def test_playbook_tc_entity(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_tc_entity(variable, value)
        result = tcex.playbook.read_tc_entity(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:b1!TCEntity', {'one': '1', 'two': 'two'}),
            ('#App:0002:b2!TCEntity', []),
            ('#App:0002:b3!TCEntity', {}),
            ('#App:0002:b4!WrongType', 'wrong type'),
        ],
    )
    def test_playbook_tc_entity_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_tc_entity(variable, value)
            assert False, f'{value} is not a valid Binary value'
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
    def test_playbook_tc_entity_array(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex.playbook.create_tc_entity_array(variable, value)
        result = tcex.playbook.read_tc_entity_array(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

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
    def test_playbook_tc_entity_array_fail(self, variable, value, tcex):
        """Test the string array method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        try:
            tcex.playbook.create_tc_entity_array(variable, value)
            assert False, f'{value} is not a valid Binary Array value'
        except RuntimeError:
            assert True
