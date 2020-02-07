# -*- coding: utf-8 -*-
"""Test the TcEx IterateOn Decorator."""
import pytest
from tcex import IterateOnArg


# pylint: disable=no-self-use
class TestIterateOnArgDecorators:
    """Test the TcEx Decorators."""

    args = None
    tcex = None

    @IterateOnArg(
        arg='colors',
        default=None,
        fail_enabled=False,
        fail_msg='Failed iterate_on_args',
        fail_on=None,
    )
    def iterate_on_arg(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('colors')

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            ('colors', b'blue', 'Binary'),
            ('colors', [b'blue'], 'BinaryArray'),
            ('colors', [b'blue', b'red'], 'BinaryArray'),
            ('colors', {'key': 'color', 'value': 'blue'}, 'KeyValue'),
            ('colors', [{'key': 'color', 'value': 'blue'}], 'KeyValueArray'),
            (
                'colors',
                [{'key': 'color', 'value': 'blue'}, {'key': 'color', 'value': 'red'}],
                'KeyValueArray',
            ),
            ('colors', 'blue', 'String'),
            ('colors', ['blue'], 'StringArray'),
            ('colors', ['blue', 'red'], 'StringArray'),
            ('colors', {'id': '123', 'type': 'Address', 'value': '1.1.1.1'}, 'TCEntity'),
            ('colors', [{'id': '123', 'type': 'Address', 'value': '1.1.1.1'}], 'TCEntityArray'),
            (
                'colors',
                [
                    {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
                'TCEntityArray',
            ),
        ],
    )
    def test_iterate_on_arg(self, arg, value, variable_type, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {arg: variable, 'tc_playbook_out_variables': [variable]}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # parse variable and add to KV store
        self.tcex.playbook.create_output(arg, value, variable_type)

        # call decorated method and get result
        result = self.iterate_on_arg()

        # results will always be an array so ensure value/expected is an array
        expected = value
        if not isinstance(expected, list):
            expected = [expected]
        assert result == expected, f'result of ({result}) does not match ({value})'

    @IterateOnArg(
        arg='colors',
        default='magenta',
        fail_enabled=False,
        fail_msg='Failed iterate_on_args',
        fail_on=None,
    )
    def iterate_on_arg_default(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('colors')

    @pytest.mark.parametrize(
        'arg,value,variable_type,expected',
        [
            # expected must have default value from decorator
            ('colors', None, 'String', []),
            ('colors', [None], 'StringArray', ['magenta']),
            ('colors', ['blue', None], 'StringArray', ['blue', 'magenta']),
        ],
    )
    def test_iterate_on_arg_default(self, arg, value, variable_type, expected, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {arg: variable, 'tc_playbook_out_variables': [variable]}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # parse variable and add to KV store
        self.tcex.playbook.create_output(arg, value, variable_type)

        # call decorated method and get result
        result = self.iterate_on_arg_default()

        assert result == expected, f'result of ({result}) does not match ({expected})'

    @IterateOnArg(
        arg='colors',
        default=None,
        fail_enabled='fail_on_error',
        fail_msg='Failed iterate_on_args',
        fail_on=[None, ''],
    )
    def iterate_on_arg_fail_on(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('colors')

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            ('colors', [None], 'StringArray'),
            ('colors', ['blue', None], 'StringArray'),
            ('colors', ['blue', ''], 'StringArray'),
        ],
    )
    def test_iterate_on_arg_fail_on(self, arg, value, variable_type, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {
            arg: variable,
            'fail_on_error': True,
            'tc_playbook_out_variables': [variable],
        }
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # parse variable and add to KV store
        self.tcex.playbook.create_output(arg, value, variable_type)

        # call decorated method and get result
        try:
            self.iterate_on_arg_fail_on()
            assert False, 'fail on value was not caught'
        except RuntimeError as e:
            assert e.args[0] == 'Failed iterate_on_args'  # must match fail_msg on decorator
