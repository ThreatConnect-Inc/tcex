# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

import pytest

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestUtils:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        out_variables = []
        setattr(tcex.args, 'tc_playbook_out_variables', ','.join(out_variables))

        # add string inputs
        string_inputs = [
            {'variable': '#App:0001:string.1!String', 'data': 'DATA'},
            {'variable': '#App:0001:string.2!String', 'data': 'This is \"a string\"'},
            {'variable': '#App:0001:string.3!String', 'data': 'two'},
        ]
        for i in string_inputs:
            tcex.playbook.create_string(i.get('variable'), i.get('data'))

        string_array_inputs = [
            {
                'variable': '#App:0001:array.1!StringArray',
                'data': ['#App:0001:string.3!String', 'three'],
            }
        ]
        for i in string_array_inputs:
            tcex.playbook.create_string_array(i.get('variable'), i.get('data'))

    @pytest.mark.parametrize(
        'variable,embedded_value,resolved_value',
        [
            (
                '#App:0001:embedded.string.1!String',
                'Test of embedded #App:0001:string.1!String in String.',
                'Test of embedded DATA in String.',
            ),
            (
                '#App:0001:embedded.string.1!String',
                '#App:0001:string.2!String inside a string.',
                'This is "a string" inside a string.',
            ),
        ],
    )
    def test_embedded_string_in_string(self, variable, embedded_value, resolved_value):
        """Test playbook embedded string in string"""
        tcex.playbook.create_string(variable, embedded_value)
        assert tcex.playbook.read(variable) == resolved_value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,embedded_value,resolved_value',
        [
            (
                '#App:0001:embedded.string_array.1!String',
                'Test of embedded #App:0001:array.1!StringArray in String.',
                '"Test of embedded ["two", "three"] in String."',
            )
        ],
    )
    def test_embedded_string_array_in_string(self, variable, embedded_value, resolved_value):
        """Test playbook embedded string array in string"""
        tcex.playbook.create_string(variable, embedded_value)
        assert tcex.playbook.read(variable) == resolved_value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,embedded_value,resolved_value',
        [
            (
                '#App:0001:embedded.string_array.2!StringArray',
                ['one', '#App:0001:string.3!String', 'three'],
                ['one', 'two', 'three'],
            )
        ],
    )
    def test_embedded_string_in_string_array(self, variable, embedded_value, resolved_value):
        """Test playbook embedded string in string array"""
        tcex.playbook.create_string_array(variable, embedded_value)
        assert tcex.playbook.read(variable) == resolved_value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,embedded_value,resolved_value',
        [
            (
                '#App:0001:embedded.string_array.3!StringArray',
                ['one', '#App:0001:array.1!StringArray', 'four'],
                ['one', 'two', 'three', 'four'],
            )
        ],
    )
    def test_embedded_string_array_in_string_array(self, variable, embedded_value, resolved_value):
        """Test playbook embedded string array in string array"""
        tcex.playbook.create_string_array(variable, embedded_value)
        assert tcex.playbook.read(variable) == resolved_value

        # tcex.playbook.delete(variable)
        # assert tcex.playbook.read(variable) is None
