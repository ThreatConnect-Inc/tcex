# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

import pytest

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        out_variables = [
            '#App:0001:one!String',
            '#App:0001:two!String',
            '#App:0001:three!String',
            '#App:0001:four!String',
            '#App:0001:a!StringArray',
        ]
        setattr(tcex.args, 'tc_playbook_out_variables', ','.join(out_variables))

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0001:one!String', '1'),
            ('#App:0001:two!String', '2'),
            ('#App:0001:three!String', '3'),
            ('#App:0001:four!String', '4'),
            ('#App:0001:a!StringArray', ['a', 'b', 'c']),
        ],
    )
    def test_create_output(self, variable, value):
        """Test playbook create output"""
        parsed_variable = tcex.playbook.parse_variable(variable)
        variable_name = parsed_variable.get('name')
        variable_type = parsed_variable.get('type')
        tcex.playbook.create_output(variable_name, value, variable_type)
        assert tcex.playbook.read(variable) == value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0002:five!String', '1'),
            ('#App:0002:six!String', '2'),
            ('#App:0002:seven!String', '3'),
            ('#App:0002:eight!String', '4'),
        ],
    )
    def test_string(self, variable, value):
        """Test playbook create output"""
        tcex.playbook.create_string(variable, value)
        assert tcex.playbook.read_string(variable) == value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            ('#App:0003:nine!StringArray', ['1', '1']),
            ('#App:0003:ten!StringArray', ['2', '2']),
            ('#App:0003:eleven!StringArray', ['3', '3']),
            ('#App:0003:twelve!StringArray', ['4', '4']),
        ],
    )
    def test_string_array(self, variable, value):
        """Test playbook create output"""
        tcex.playbook.create_string_array(variable, value)
        assert tcex.playbook.read_string_array(variable) == value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None
