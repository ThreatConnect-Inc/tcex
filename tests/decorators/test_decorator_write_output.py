# -*- coding: utf-8 -*-
"""Test the TcEx WriteOutput Decorator."""
# third-party
import pytest

# first-party
from tcex import WriteOutput


# pylint: disable=no-self-use
class TestWriteOutputDecorators:
    """Test the TcEx WriteOutput Decorators."""

    args = None
    tcex = None

    @WriteOutput(key='color', variable_type='String', default=None, overwrite=True)
    def write_output_string(self, color):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return color

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            ('color', 'red', 'String'),
            ('color', 'blue', 'String'),
            ('color', 'green', 'String'),
            ('color', None, 'String'),
        ],
    )
    def test_write_output_string(self, arg, value, variable_type, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {arg: variable, 'tc_playbook_out_variables': [variable]}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # run decorated method
        self.write_output_string(value)

        # trigger write of all output variables to kv store
        self.tcex.playbook.write_output()

        assert self.tcex.playbook.read(variable) == value

    @WriteOutput(key='color', variable_type='String', default='red', overwrite=False)
    def write_output_string_default(self, color):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return color

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            ('color', 'red', 'String'),
            ('color', 'blue', 'String'),
            ('color', 'green', 'String'),
            ('color', None, 'String'),
        ],
    )
    def test_write_output_string_default(self, arg, value, variable_type, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {arg: variable, 'tc_playbook_out_variables': [variable]}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # run decorated method
        self.write_output_string_default(value)
        self.write_output_string_default('overwrite')  # this call should get ignored

        # trigger write of all output variables to kv store
        self.tcex.playbook.write_output()
        expected = value or 'red'  # must match default arg on decorator

        result = self.tcex.playbook.read(variable)
        assert result == expected, f'result of ({result}) does not match ({expected})'

    @WriteOutput(key='color', variable_type='String', default='red', overwrite=True)
    def write_output_string_overwrite(self, color):
        """Test fail on input decorator with no arg value (use first arg input)."""
        return color

    @pytest.mark.parametrize(
        'arg,value,variable_type',
        [
            ('color', 'red', 'String'),
            ('color', 'blue', 'String'),
            ('color', 'green', 'String'),
            ('color', None, 'String'),
        ],
    )
    def test_write_output_string_overwrite(self, arg, value, variable_type, playbook_app):
        """Test ReadArg decorator.

        Args:
            playbook_app (callable, fixture): The playbook_app fixture.
        """
        variable = f'#App:0001:{arg}!{variable_type}'
        config_data = {arg: variable, 'tc_playbook_out_variables': [variable]}
        self.tcex = playbook_app(config_data=config_data).tcex
        self.args = self.tcex.args

        # run decorated method
        self.write_output_string_overwrite(value)
        expected = 'red'
        self.write_output_string_overwrite(expected)

        # trigger write of all output variables to kv store
        self.tcex.playbook.write_output()
        expected = 'red'  # must match default arg on decorator

        result = self.tcex.playbook.read(variable)
        assert result == expected, f'result of ({result}) does not match ({expected})'
