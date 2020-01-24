# -*- coding: utf-8 -*-
"""Test the TcEx Batch Module."""
import pytest


class TestEmbedded:
    """Test the TcEx Batch Module."""

    @staticmethod
    def stage_data(tcex):
        """Configure setup before all tests."""
        out_variables = []
        setattr(tcex.args, 'tc_playbook_out_variables', ','.join(out_variables))

        # add String inputs
        string_inputs = [
            {'variable': '#App:0001:string.1!String', 'data': 'DATA'},
            {'variable': '#App:0001:string.2!String', 'data': 'This is \"a string\"'},
            {'variable': '#App:0001:string.3!String', 'data': 'two'},
            {'variable': '#App:0001:string.4!String', 'data': 'one\ntwo\n'},
            {'variable': '#App:0001:string.5!String', 'data': r'\snow or later\s'},
            {'variable': '#App:0001:string.6!String', 'data': r'\snow is not \\snow.\s'},
            {'variable': '#App:0001:string.7!String', 'data': r'invalid json char " \\'},
            {
                'variable': '#App:0001:string.8!String',
                'data': r'Json Reserved Characters: \\\\" \n \r \f \b \t \\',
            },
        ]
        for i in string_inputs:
            tcex.playbook.create_string(i.get('variable'), i.get('data'))

        # add StringArray inputs
        string_array_inputs = [
            {'variable': '#App:0001:array.1!StringArray', 'data': ['two', 'three']},
            {'variable': '#App:0001:array.2!StringArray', 'data': ['three', 'four']},
        ]
        for i in string_array_inputs:
            tcex.playbook.create_string_array(i.get('variable'), i.get('data'))

        # add KeyValue inputs
        keyvalue_inputs = [
            {
                'variable': '#App:0001:keyvalue.1!KeyValue',
                'data': {'key': 'kv1', 'value': 'kv1 value'},
            },
            {
                'variable': '#App:0001:keyvalue.2!KeyValue',
                'data': {'key': 'kv2', 'value': 'kv2 value'},
            },
            {
                'variable': '#App:0001:keyvalue.3!KeyValue',
                'data': {'key': 'kv3', 'value': 'kv3 value'},
            },
        ]
        for i in keyvalue_inputs:
            tcex.playbook.create_key_value(i.get('variable'), i.get('data'))

        # add KeyValueArray inputs
        keyvalue_array_inputs = [
            {
                'variable': '#App:0001:keyvalue.array.1!KeyValueArray',
                'data': [
                    {'key': 'kva1', 'value': 'kva1 value'},
                    {'key': 'kva2', 'value': 'kva2 value'},
                ],
            }
        ]
        for i in keyvalue_array_inputs:
            tcex.playbook.create_key_value_array(i.get('variable'), i.get('data'))

    @pytest.mark.parametrize(
        'embedded_value,expected',
        [
            (
                (
                    '{\n\"trackingID\": 12345,\n\"title\": \"#App:0001:string.7!String\",\n'
                    '\"comments\": \"#App:0001:string.8!String\",\n\"requestor\": '
                    '\"ThreatConnect Playbook\"}'
                ),
                (
                    '{\n\"trackingID\": 12345,\n\"title\": \"invalid json char \" \\",\n'
                    '\"comments\": \"Json Reserved Characters: \\\\" \n \r \f \b \t '
                    '\\",\n\"requestor\": \"ThreatConnect Playbook\"}'
                ),
            ),
            # test \s replacement
            (r'\stest', r' test'),
            (r'test\s', r'test '),
            (r'\stest\s', r' test '),
            (r'\\stest', r'\stest'),
            (r'test\\s', r'test\s'),
            (r'\\\somedir', r'\\somedir'),
            (r'\snow\sor\slater\s', ' now or later '),
            (
                '{"numbers": "#App:0001:string.4!String three\n\r"}',
                '{"numbers": "one\ntwo\n three\n\r"}',
            ),
            # String Test: new lines
            ('#App:0001:string.4!String', 'one\ntwo\n'),
            # String Test: escaped \n
            ('#App:0001:string.5!String', r'\snow or later\s'),
            # String Test: \s replacement
            ('#App:0001:string.6!String', r'\snow is not \\snow.\s'),
            # String Test: String in String
            ('This is #App:0001:string.1!String in a String.', 'This is DATA in a String.'),
            # String Test: StringArray in String
            (
                'This is #App:0001:array.1!StringArray in a String.',
                'This is ["two", "three"] in a String.',
            ),
            # String Test: KeyValue in String
            (
                'This is #App:0001:keyvalue.1!KeyValue in a String.',
                'This is {"key": "kv1", "value": "kv1 value"} in a String.',
            ),
            # String Test: KeyValueArray in String
            (
                'This is #App:0001:keyvalue.array.1!KeyValueArray in a String.',
                (
                    'This is [{"key": "kva1", "value": "kva1 value"}, '
                    '{"key": "kva2", "value": "kva2 value"}] in a String.'
                ),
            ),
            # String Test: String and StringArray in String
            (
                'This is #App:0001:string.1!String and #App:0001:array.1!StringArray in '
                'a String.',
                'This is DATA and ["two", "three"] in a String.',
            ),
            # String Test: service now use case
            ('{"work_notes": "#App:0001:string.4!String"}', '{"work_notes": "one\ntwo\n"}'),
            # KeyValueArray Test: Nested KeyValue
            (
                '{"key": "one", "value": #App:0001:keyvalue.1!KeyValue}',
                '{"key": "one", "value": {"key": "kv1", "value": "kv1 value"}}',
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
                    '    "KeyValue": {"key": "kv1", "value": "kv1 value"},'
                    '    "KeyValueArray": '
                    '[{"key": "kva1", "value": "kva1 value"}, '
                    '{"key": "kva2", "value": "kva2 value"}],'
                    '    "String": "DATA",'
                    '    "StringArray": ["two", "three"]'
                    '}'
                ),
            ),
            # StringArray Test: String in StringArray
            ('#App:0001:array.1!StringArray', ['two', 'three']),
        ],
    )
    def test_embedded_read_string(self, embedded_value, expected, tcex):
        """Test the create output method of Playbook module.

        Args:
            variable (str): The key/variable to create in Key Value Store.
            value (str): The value to store in Key Value Store.
            tcex (TcEx, fixture): The tcex fixture.
        """
        self.stage_data(tcex)
        result = tcex.playbook.read(embedded_value)
        assert result == expected, f'result of ({result}) does not match ({expected})'
