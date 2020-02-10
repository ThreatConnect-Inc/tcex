# -*- coding: utf-8 -*-
"""Test the TcEx ReadArg Decorator."""
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
