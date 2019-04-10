# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""

import pytest

from ..tcex_init import tcex


# pylint: disable=R0201,W0201
class TestEmbedded:
    """Test the TcEx Batch Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        out_variables = []
        setattr(tcex.args, 'tc_playbook_out_variables', ','.join(out_variables))

        # add String inputs
        string_inputs = [
            {'variable': '#App:0001:string.1!String', 'data': 'DATA'},
            {'variable': '#App:0001:string.2!String', 'data': 'This is \"a string\"'},
            {'variable': '#App:0001:string.3!String', 'data': 'two'},
            {'variable': '#App:0001:string.4!String', 'data': 'one\ntwo\n'},
        ]
        for i in string_inputs:
            tcex.playbook.create_string(i.get('variable'), i.get('data'))

        # add StringArray inputs
        string_array_inputs = [
            {
                'variable': '#App:0001:array.1!StringArray',
                'data': ['#App:0001:string.3!String', 'three'],
            }
        ]
        for i in string_array_inputs:
            tcex.playbook.create_string_array(i.get('variable'), i.get('data'))

        # add KeyValue inputs
        keyvalue_inputs = [
            {
                'variable': '#App:0001:keyvalue.1!KeyValue',
                'data': {'key': 'kv1', 'value': '#App:0001:string.3!String'},
            },
            {
                'variable': '#App:0001:keyvalue.2!KeyValue',
                'data': {'key': 'kv1', 'value': '#App:0001:array.1!StringArray'},
            },
        ]
        for i in keyvalue_inputs:
            tcex.playbook.create_key_value(i.get('variable'), i.get('data'))

        # add KeyValueArray inputs
        keyvalue_array_inputs = [
            {
                'variable': '#App:0001:keyvalue.array.1!KeyValueArray',
                'data': [
                    {'key': 'kv.string', 'value': '#App:0001:string.3!String'},
                    {'key': 'kv.string.array', 'value': '#App:0001:array.1!StringArray'},
                ],
            }
        ]
        for i in keyvalue_array_inputs:
            tcex.playbook.create_key_value_array(i.get('variable'), i.get('data'))

    @pytest.mark.parametrize(
        'embedded_value,resolved_value',
        [
            ('{"work_notes": "#App:0001:string.4!String"}', '{"work_notes": "one\\ntwo\\n"}'),
            (
                '{"key": "one", "value": #App:0001:keyvalue.1!KeyValue}',
                '{"key": "one", "value": {"value": "two", "key": "kv1"}}',
            ),
            (
                (
                    '{'
                    '    "KeyValue": #App:0001:keyvalue.1!KeyValue,'
                    '    "KeyValueArray": #App:0001:keyvalue.array.1!KeyValueArray,'
                    '    "String": "#App:0001:string.1!String",'
                    '    "StringArray": #App:0001:array.1!StringArray'
                    '}'
                ),
                (
                    '{'
                    '    "KeyValue": {"value": "two", "key": "kv1"},'
                    '    "KeyValueArray": '
                    '[{"value": "two", "key": "kv.string"}, '
                    '{"value": ["two", "three"], "key": "kv.string.array"}],'
                    '    "String": "DATA",'
                    '    "StringArray": ["two", "three"]'
                    '}'
                ),
            ),
            ('#App:0001:array.1!StringArray', ['two', 'three']),
        ],
    )
    def test_embedded_read_string(self, embedded_value, resolved_value):
        """Test playbook embedded string in string"""
        print(tcex.playbook.read(embedded_value))
        assert tcex.playbook.read(embedded_value) == resolved_value

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
            (
                '#App:0001:embedded.string.1!String',
                '{"work_notes": "#App:0001:string.4!String"}',
                '{"work_notes": "one\ntwo\n"}',
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

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,embedded_value,resolved_value',
        [
            (
                '#App:0001:embedded.keyvalue.1!KeyValue',
                {'key': 'one', 'value': '#App:0001:string.3!String'},
                {'key': 'one', 'value': 'two'},
            )
        ],
    )
    def test_embedded_string_in_keyvalue(self, variable, embedded_value, resolved_value):
        """Test playbook embedded string array in string array"""
        tcex.playbook.create_key_value(variable, embedded_value)
        assert tcex.playbook.read(variable) == resolved_value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    @pytest.mark.parametrize(
        'variable,embedded_value,resolved_value',
        [
            (
                '#App:0001:embedded.keyvalue.1!KeyValue',
                {'key': 'one', 'value': '#App:0001:array.1!StringArray'},
                {'key': 'one', 'value': ['two', 'three']},
            )
        ],
    )
    def test_embedded_string_array_in_keyvalue(self, variable, embedded_value, resolved_value):
        """Test playbook embedded string array in string array"""
        tcex.playbook.create_key_value(variable, embedded_value)
        assert tcex.playbook.read(variable) == resolved_value

        tcex.playbook.delete(variable)
        assert tcex.playbook.read(variable) is None

    # @pytest.mark.parametrize(
    #     'variable,embedded_value,resolved_value',
    #     [
    #         (
    #             '#App:0001:embedded.keyvalue.1!KeyValue',
    #             {'key': 'one', 'value': '#App:0001:keyvalue.1!KeyValue'},
    #             {'key': 'one', 'value': {'value': 'two', 'key': 'kv1'}},
    #         )
    #     ],
    # )
    # def test_embedded_keyvalue_in_keyvalue(self, variable, embedded_value, resolved_value):
    #     """Test playbook embedded string array in string array"""
    #     tcex.playbook.create_key_value(variable, embedded_value)
    #     print(tcex.playbook.read(variable))
    #     # assert tcex.playbook.read(variable) == resolved_value

    #     tcex.playbook.delete(variable)
    #     assert tcex.playbook.read(variable) is None
