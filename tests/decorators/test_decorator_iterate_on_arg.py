# -*- coding: utf-8 -*-
"""Test the TcEx IterateOn Decorator."""
# third-party
import pytest

# first-party
from tcex import IterateOnArg, OnException


# pylint: disable=no-self-use
class TestIterateOnArgDecorators:
    """Test the TcEx Decorators."""

    args = None
    tcex = None
    exit_message = None

    @IterateOnArg(
        arg='colors',
        default=None,
        fail_enabled=True,
        fail_msg='Failed iterate_on_args',
        fail_msg_property='fail_msg',
        fail_on=[None],
    )
    @OnException()
    def iterate_on_arg(self, ret_val, colors, _array_length=None, _index=None):
        """Test fail on input decorator with no arg value (use first arg input)."""
        if ret_val == 'colors':
            return colors

        if ret_val == '_array_length':
            return _array_length

        if ret_val == '_index':
            return _index

        return None

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
    def test_iterate_on_arg_color(self, arg, value, variable_type, playbook_app):
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
        result = self.iterate_on_arg(ret_val='colors')  # pylint: disable=no-value-for-parameter

        # results will always be an array so ensure value/expected is an array
        expected = value
        if not isinstance(expected, list):
            expected = [expected]
        assert result == expected, f'result of ({result}) does not match ({expected})'

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
    def test_iterate_on_arg_array_length(self, arg, value, variable_type, playbook_app):
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
        result = self.iterate_on_arg(  # pylint: disable=no-value-for-parameter
            ret_val='_array_length'
        )

        # results will always be an array so ensure value/expected is an array
        expected = value
        if not isinstance(expected, list):
            expected = [expected]
        assert result[0] == len(
            expected
        ), f'array length of {result} does not match length of expected'

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
    def test_iterate_on_arg_index(self, arg, value, variable_type, playbook_app):
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
        result = self.iterate_on_arg(ret_val='_index')  # pylint: disable=no-value-for-parameter

        # results will always be an array so ensure value/expected is an array
        expected = value
        if not isinstance(expected, list):
            expected = [expected]
        assert (result[-1] + 1) == len(
            expected
        ), f'index of {result[-1]} does not match length of expected'

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
            ('colors', None, 'String', ['magenta']),
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
        except SystemExit:
            assert self.exit_message == 'Failed iterate_on_args'  # must match fail_msg on decorator
