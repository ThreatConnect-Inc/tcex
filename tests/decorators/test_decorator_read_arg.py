"""Test the TcEx ReadArg Decorator."""
# third-party
import pytest

# first-party
from tcex import ReadArg

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

    @ReadArg('color', fail_on=[None, ''], fail_enabled=True)
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
            assert (
                self.exit_message
                == 'Invalid value (None) found for "Color": "Color" (color) cannot be in [None, ""]'
            )

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
        'fruit', fail_on=[None, ''], fail_enabled='fail_on_error',
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
            assert (
                self.exit_message
                == 'Invalid value (None) found for "Fruit": "Fruit" (fruit) cannot be in [None, ""]'
            )

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

    @ReadArg('color', strip_values=True)
    def read_arg_strip(self, **kwargs):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return kwargs.get('color')

    def test_read_arg_strip(self, playbook_app):
        """Test the strip_values option.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': ' red '}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        assert self.read_arg_strip() == config_data.get('color').strip()

    def test_read_arg_strip_null(self, playbook_app):
        """Test strip_values option handling of null values.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': None}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        assert self.read_arg_strip() == config_data.get('color')

    @pytest.mark.parametrize(
        'variable,value', [('#App:0001:colours!StringArray', [' red ', ' blue '],)],
    )
    def test_read_arg_strip_string_array(self, variable, value, playbook_app):
        """Test the strip_values handling of string arrays.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': variable}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.tcex.playbook.create_string_array(variable, value)
        self.args = self.tcex.args
        assert self.read_arg_strip() == [c.strip() for c in value]

    @pytest.mark.parametrize(
        'variable,value', [('#App:0001:colours!KeyValue', {'key': 'foo', 'value': 'bar'},)],
    )
    def test_read_arg_strip_unsupported_type(self, variable, value, playbook_app):
        """Test the strip_values handling of unsupported types.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        config_data = {'color': variable}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.tcex.playbook.create_key_value(variable, value)
        self.args = self.tcex.args
        assert self.read_arg_strip() == value

    @ReadArg(
        'color',
        fail_on=[''],
        to_float=True,
        to_int={'allow_none': True},
        equal_to=123,
        in_range={'min': 100, 'max': 200},
        less_than=150,
    )
    def read_arg_validators(self, **kwargs):
        """Test various validators and transforms."""
        return kwargs.get('color')

    @ReadArg(
        'color',
        fail_on=[''],
        to_float=True,
        to_int={'allow_none': True},
        equal_to=123,
        in_range={'min': 100, 'max': 200},
        less_than=150,
        fail_msg='Custom fail msg.',
    )
    def read_arg_validators_Fail_msg(self, **kwargs):
        """Test various validators and transforms."""
        return kwargs.get('color')

    @ReadArg('color', fail_on=[''], to_int=[], equal_to=123, in_range=[100, 200], less_than=150)
    def read_arg_validators_diff(self, **kwargs):
        """functionally the same as above but uses different input methods to exercise code."""
        return kwargs.get('color')

    def test_validators(self, playbook_app):
        """Test validators happy-path."""
        config_data = {'color': '123'}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        assert self.read_arg_validators() == 123

    @pytest.mark.parametrize(
        'variable,value', [('#App:0001:colours!String', 123)],
    )
    def test_validators_string(self, variable, value, playbook_app):
        """Test a string input that should pass."""
        config_data = {'color': variable}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.tcex.playbook.create_string(variable, value)
        self.args = self.tcex.args
        assert self.read_arg_validators() == value

    @pytest.mark.parametrize(
        'variable,value', [('#App:0001:colours!StringArray', [123, 123])],
    )
    def test_validators_string_array(self, variable, value, playbook_app):
        """Test a string array."""
        config_data = {'color': variable}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.tcex.playbook.create_string_array(variable, value)
        self.args = self.tcex.args
        assert self.read_arg_validators_diff() == value

    def test_validators_fail_on(self, playbook_app):
        """Test that fail_on still works."""
        config_data = {'color': ''}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        try:
            self.read_arg_validators()
            assert False, 'Should have failed!'
        except SystemExit:
            assert (
                self.exit_message
                == 'Invalid value ("") found for "Color": "Color" (color) must be a float.'
            )

    def test_validators_fail_msg(self, playbook_app):
        """Test validators that fail."""
        config_data = {'color': '90'}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        try:
            self.read_arg_validators_Fail_msg()
            assert False, 'Should have failed!'
        except SystemExit:
            assert self.exit_message == 'Custom fail msg.'

    def test_transforms_fail_msg(self, playbook_app):
        """Test validators that fail."""
        config_data = {'color': 'abc'}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args
        try:
            self.read_arg_validators_Fail_msg()
            assert False, 'Should have failed!'
        except SystemExit:
            assert self.exit_message == 'Custom fail msg.'
