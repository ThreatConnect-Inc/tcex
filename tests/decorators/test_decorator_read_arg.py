# -*- coding: utf-8 -*-
"""Test the TcEx ReadArg Decorator."""
from tcex import ReadArg

import pytest


# pylint: disable=no-self-use
class TestReadArgDecorators:
    """Test the TcEx ReadArg Decorators."""

    args = None
    exit_message = None
    tcex = None

    @ReadArg('color')
    def read_arg_single(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('color')

    def test_read_arg_single(self, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': 'red'}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        assert self.read_arg_single() == config_data.get('color')

    @ReadArg(
        'color', fail_on=[None, ''], fail_enabled=True, fail_msg='Invalid value provided for color.'
    )
    def read_arg_single_fail_on(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('color')

    def test_read_arg_single_fail_on(self, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': None}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        try:
            self.read_arg_single_fail_on()
            assert False, 'fail on value was not caught'
        except SystemExit as e:
            assert e.code == 1
            assert self.exit_message == 'Invalid value provided for color.'

    @ReadArg('color')
    @ReadArg('fruit')
    def read_arg_double(self, color, fruit):
        """Test fail on input decorator with no arg value (use first arg input)."""
        # return kwargs.get('color'), kwargs.get('fruit')
        return color, fruit

    def test_read_arg_double(self, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': 'red', 'fruit': 'tomato'}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        assert self.read_arg_double(**{}) == (config_data.get('color'), config_data.get('fruit'))

    @ReadArg('color')
    @ReadArg(
        'fruit',
        fail_on=[None, ''],
        fail_enabled='fail_on_error',
        fail_msg='Invalid value provided for fruit.',
    )
    def read_arg_double_fail_on(self, color, fruit):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return color, fruit

    def test_read_arg_double_fail_on(self, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': 'blue', 'fruit': None, 'fail_on_error': True}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        try:
            self.read_arg_double_fail_on(**{})
            assert False, 'fail on value was not caught'
        except SystemExit as e:
            assert e.code == 1
            assert self.exit_message == 'Invalid value provided for fruit.'

    @ReadArg('color')
    @ReadArg('fruit', default='pear')
    @ReadArg(
        'number',
        array=False,
        fail_on=['', None],
        fail_enabled='fail_on_error',
        fail_msg='number was not right',
    )
    def read_arg_triple(self, color, fruit, number):
        """Test fail on input decorator with no arg value (use first arg input)."""
        # return kwargs.get('color'), kwargs.get('fruit')
        return color, fruit, number

    def test_read_arg_triple(self, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': 'blue', 'fail_on_error': False, 'fruit': None, 'number': '42'}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        assert self.read_arg_triple(**{}) == (
            config_data.get('color'),
            'pear',
            config_data.get('number'),
        )

    @ReadArg('color', fail_enabled=False)
    def read_arg_not_in_namespace(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('color')

    def test_read_arg_not_in_namespace(self, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        self.tcex = playbook_app().tcex
        self.args = self.tcex.args
        assert self.read_arg_not_in_namespace() is None

    @ReadArg('color', fail_enabled=True, fail_msg='Invalid value provided for color.')
    def read_arg_not_in_namespace_fail(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('color')

    def test_read_arg_not_in_namespace_fail(self, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        self.tcex = playbook_app().tcex
        self.args = self.tcex.args
        try:
            self.read_arg_not_in_namespace_fail()
            assert False, 'AttributeError for non existing arg not caught'
        except SystemExit as e:
            assert e.code == 1
            assert self.exit_message == 'Invalid value provided for color.'

    @ReadArg('groups', group_ids=True)
    def read_arg_group_ids(self, groups):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return groups

    @pytest.mark.parametrize(
        'variable,value',
        [
            (
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Adversary', 'value': 'adv-001'},
                    {'id': '002', 'type': 'Adversary', 'value': 'adv-002'},
                ],
            )
        ],
    )
    def test_read_arg_group_ids(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'groups': variable}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.tcex.playbook.create_tc_entity_array(variable, value)
        self.args = self.tcex.args

        results = self.read_arg_group_ids(**{})
        expected = [d.get('id') for d in value]
        assert results == expected, f'results {results} does not match expected {expected}'

    @ReadArg('groups', group_values=True)
    def read_arg_group_values(self, groups):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return groups

    @pytest.mark.parametrize(
        'variable,value',
        [
            (
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Adversary', 'value': 'adv-001'},
                    {'id': '002', 'type': 'Adversary', 'value': 'adv-002'},
                ],
            )
        ],
    )
    def test_read_arg_group_values(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'groups': variable}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.tcex.playbook.create_tc_entity_array(variable, value)
        self.args = self.tcex.args

        results = self.read_arg_group_values(**{})
        expected = [d.get('value') for d in value]
        assert results == expected, f'results {results} does not match expected {expected}'

    @ReadArg('indicators', indicator_values=True)
    def read_arg_indicator_values(self, indicators):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return indicators

    @pytest.mark.parametrize(
        'variable,value',
        [
            (
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
            )
        ],
    )
    def test_read_arg_indicator_values(self, variable, value, playbook_app):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'indicators': variable}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.tcex.playbook.create_tc_entity_array(variable, value)
        self.args = self.tcex.args

        results = self.read_arg_indicator_values(**{})
        expected = [d.get('value') for d in value]
        assert results == expected, f'results {results} does not match expected {expected}'
