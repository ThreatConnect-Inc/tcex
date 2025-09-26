"""TestPlaybookEmbeddedVariable for TcEx App Playbook Embedded Variable Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Embedded Variable Module,
specifically testing embedded variable functionality including string replacement, variable
expansion, JSON handling, escape character processing, and various data type embedding
scenarios across different playbook variable types and formats.

Classes:
    TestPlaybookEmbeddedVariable: Test class for TcEx App Playbook Embedded Variable Module
        functionality

TcEx Module Tested: app.playbook.playbook_read
"""


from typing import Any


import pytest


from tcex import TcEx
from tcex.app.playbook import Playbook


class TestPlaybookEmbeddedVariable:
    """TestPlaybookEmbeddedVariable for TcEx App Playbook Embedded Variable Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Embedded Variable Module,
    covering various embedded variable scenarios including string replacement patterns,
    variable expansion, JSON data handling, escape character processing, and complex
    nested variable embedding across different playbook variable types.
    """

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method is called before each test method to prepare the test environment
        for embedded variable testing scenarios.
        """
        # setup method for future use if needed

    @staticmethod
    def stage_data(tcex: TcEx) -> None:
        """Stage test data for embedded variable testing.

        This utility method sets up various playbook variables with different data types
        and values to test embedded variable functionality including strings, string arrays,
        key-value pairs, and key-value arrays with various escape characters and formats.

        Args:
            tcex: TcEx instance with playbook functionality configured
        """
        out_variables = []
        tcex.inputs.model.tc_playbook_out_variables = ','.join(out_variables)  # type: ignore
        playbook = tcex.app.playbook

        # add String inputs
        string_inputs = [
            {'variable': '#App:0001:string.1!String', 'data': 'DATA'},
            {'variable': '#App:0001:string.2!String', 'data': 'This is "a string"'},
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
            playbook.create.string(i['variable'], i['data'], when_requested=False)

        # add StringArray inputs
        string_array_inputs = [
            {'variable': '#App:0001:array.1!StringArray', 'data': ['two', 'three']},
            {'variable': '#App:0001:array.2!StringArray', 'data': ['three', 'four']},
        ]
        for i in string_array_inputs:
            playbook.create.string_array(i['variable'], i['data'], when_requested=False)

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
            playbook.create.key_value(i['variable'], i['data'], when_requested=False)

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
            playbook.create.key_value_array(i['variable'], i['data'], when_requested=False)

    @pytest.mark.parametrize(
        'embedded_value,expected',
        [
            # test \s replacement
            pytest.param(r'\stest', r' test', id='pass-backslash-s-start'),
            pytest.param(r'test\s', r'test ', id='pass-backslash-s-end'),
            pytest.param(r'\stest\s', r' test ', id='pass-backslash-s-both'),
            pytest.param(r'\\stest', r'\stest', id='pass-escaped-backslash-s-start'),
            pytest.param(r'test\\s', r'test\s', id='pass-escaped-backslash-s-end'),
            pytest.param(r'\\\somedir', r'\\somedir', id='pass-escaped-backslash-somedir'),
            pytest.param(r'\snow\sor\slater\s', ' now or later ', id='pass-multiple-backslash-s'),
            pytest.param(
                '{"numbers": "#App:0001:string.4!String three\n\r"}',
                '{"numbers": "one\ntwo\n three\n\r"}',
                id='pass-json-with-embedded-string',
            ),
            # String Test: new lines
            pytest.param('#App:0001:string.4!String', 'one\ntwo\n', id='pass-string-with-newlines'),
            # String Test: escaped \n
            pytest.param(
                '#App:0001:string.5!String', r'\snow or later\s', id='pass-string-with-escaped-n'
            ),
            # String Test: \s replacement
            pytest.param(
                '#App:0001:string.6!String',
                r'\snow is not \\snow.\s',
                id='pass-string-with-backslash-s',
            ),
            # String Test: String in String
            pytest.param(
                'This is #App:0001:string.1!String in a String.',
                'This is DATA in a String.',
                id='pass-string-embedded-in-string',
            ),
            # String Test: StringArray in String
            pytest.param(
                'This is #App:0001:array.1!StringArray in a String.',
                'This is ["two", "three"] in a String.',
                id='pass-stringarray-embedded-in-string',
            ),
            # String Test: KeyValue in String
            pytest.param(
                'This is #App:0001:keyvalue.1!KeyValue in a String.',
                'This is {"key": "kv1", "value": "kv1 value"} in a String.',
                id='pass-keyvalue-embedded-in-string',
            ),
            # String Test: KeyValueArray in String
            pytest.param(
                'This is #App:0001:keyvalue.array.1!KeyValueArray in a String.',
                (
                    'This is [{"key": "kva1", "value": "kva1 value"}, '
                    '{"key": "kva2", "value": "kva2 value"}] in a String.'
                ),
                id='pass-keyvaluearray-embedded-in-string',
            ),
            # String Test: String and StringArray in String
            pytest.param(
                'This is #App:0001:string.1!String and #App:0001:array.1!StringArray in a String.',
                'This is DATA and ["two", "three"] in a String.',
                id='pass-mixed-variables-embedded-in-string',
            ),
            # String Test: service now use case
            pytest.param(
                '{"work_notes": "#App:0001:string.4!String"}',
                '{"work_notes": "one\ntwo\n"}',
                id='pass-servicenow-work-notes',
            ),
            # KeyValueArray Test: Nested KeyValue
            pytest.param(
                '{"key": "one", "value": #App:0001:keyvalue.1!KeyValue}',
                '{"key": "one", "value": {"key": "kv1", "value": "kv1 value"}}',
                id='pass-nested-keyvalue-in-json',
            ),
            pytest.param(
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
                id='pass-complex-json-with-multiple-embedded-types',
            ),
            # StringArray Test: String in StringArray
            pytest.param(
                '#App:0001:array.1!StringArray', ['two', 'three'], id='pass-stringarray-direct'
            ),
        ],
    )
    def test_embedded_read_string(self, embedded_value: str, expected: Any, tcex: TcEx) -> None:
        """Test Embedded Read String for TcEx App Playbook Embedded Variable Module.

        This test case verifies that embedded variable functionality works correctly
        by testing various embedded variable patterns including string replacement,
        variable expansion, JSON handling, escape character processing, and complex
        nested variable scenarios across different playbook variable types.

        Parameters:
            embedded_value: The string containing embedded variables to test
            expected: The expected result after variable expansion and processing

        Fixtures:
            tcex: TcEx instance with playbook functionality configured
        """
        playbook: Playbook = tcex.app.playbook
        self.stage_data(tcex)
        result = playbook.read.variable(embedded_value)
        # print('result', result)
        # print('\n')
        # print('expected', expected)
        assert result == expected, f'result of ({result}) does not match ({expected})'
