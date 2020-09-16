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

    @IterateOnArg(
        'colors',
        fail_on=[''],
        to_float=True,
        to_int={'allow_none': True},
        equal_to=123,
        in_range={'min': 100, 'max': 200},
        less_than=150,
        default='123',
        fail_enabled=True,
    )
    def iterate_on_arg_validators(self, **kwargs):
        """Test various validators and transforms."""
        return kwargs.get('colors')

    @IterateOnArg(
        'colors',
        fail_on=[''],
        to_float=True,
        to_int={'allow_none': True},
        equal_to=123,
        in_range={'min': 100, 'max': 200},
        less_than=150,
        fail_msg='Custom fail msg.',
        fail_enabled=True,
    )
    def iterate_on_arg_validators_fail_msg(self, **kwargs):
        """Test various validators and transforms."""
        return kwargs.get('colors')

    @IterateOnArg(
        'colors', fail_on=[''], to_int=[], equal_to=123, in_range=[100, 200], less_than=150
    )
    def iterate_on_arg_validators_diff(self, **kwargs):
        """functionally the same as above but uses different input methods to exercise code."""
        return kwargs.get('colors')

    @pytest.mark.parametrize(
        'arg,value,variable_type,expected',
        [
            # expected must have default value from decorator
            ('colors', None, 'String', [123]),
            ('colors', [None], 'StringArray', [123]),
            ('colors', ['123', None], 'StringArray', [123, 123]),
        ],
    )
    def test_iterate_on_arg_validators(self, arg, value, variable_type, expected, playbook_app):
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
        result = self.iterate_on_arg_validators()

        assert result == expected, f'result of ({result}) does not match ({expected})'

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            # expected must have default value from decorator
            ('colors', ['135'], 'StringArray'),
        ],
    )
    def test_iterate_on_arg_validators_fail(self, arg, value, variable_type, playbook_app):
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
        try:
            self.iterate_on_arg_validators()
            assert False, 'Should have failed!'
        except SystemExit:
            assert (
                self.exit_message
                == 'Invalid value (135) found for "Colors": "Colors" (colors) is not equal to 123'
            )

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            # expected must have default value from decorator
            ('colors', ['90'], 'StringArray')
        ],
    )
    def test_validators_fail_msg(self, arg, value, variable_type, playbook_app):
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
        try:
            self.iterate_on_arg_validators_fail_msg()
            assert False, 'Should have failed!'
        except SystemExit:
            assert self.exit_message == 'Custom fail msg.'

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            # expected must have default value from decorator
            ('colors', ['abc'], 'StringArray',)
        ],
    )
    def test_transforms_fail_msg(self, arg, value, variable_type, playbook_app):
        """Test fail_msg for transfomrs."""
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {arg: variable, 'tc_playbook_out_variables': [variable]}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # parse variable and add to KV store
        self.tcex.playbook.create_output(arg, value, variable_type)

        # call decorated method and get result
        try:
            self.iterate_on_arg_validators_fail_msg()
            assert False, 'Should have failed!'
        except SystemExit:
            assert self.exit_message == 'Custom fail msg.'

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            # expected must have default value from decorator
            ('colors', ['abc'], 'StringArray',)
        ],
    )
    def test_transforms_fail(self, arg, value, variable_type, playbook_app):
        """Test fail_msg for transfomrs."""
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {arg: variable, 'tc_playbook_out_variables': [variable]}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # parse variable and add to KV store
        self.tcex.playbook.create_output(arg, value, variable_type)

        # call decorated method and get result
        try:
            self.iterate_on_arg_validators()
            assert False, 'Should have failed!'
        except SystemExit:
            assert (
                self.exit_message
                == 'Invalid value ("abc") found for "Colors": "Colors" (colors) must be a float.'
            )
