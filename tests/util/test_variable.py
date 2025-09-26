"""TestVariable for testing Variable utility functions.

This module contains comprehensive test cases for the Variable utility class,
which handles parsing and validation of playbook and TC variables in the TcEx framework.

Classes:
    TestVariable: Test suite for Variable utility functionality

TcEx Module Tested: tcex.util.variable
"""


import re
from typing import Any


import pytest


from tcex.util.variable import Variable


class TestVariable:
    """TestVariable for testing Variable utility functions.

    This test class provides comprehensive test coverage for the Variable utility class,
    including tests for playbook variable parsing, TC variable validation, type checking,
    and pattern matching functionality.
    """

    variables = Variable()

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param(
                '#App:0001:binary!Binary',
                {'app_type': 'App', 'job_id': '0001', 'key': 'binary', 'type': 'Binary'},
                id='pass-binary-variable-model',
            ),
            pytest.param(
                '#App:0001:binary_array!BinaryArray',
                {'app_type': 'App', 'job_id': '0001', 'key': 'binary_array', 'type': 'BinaryArray'},
                id='pass-binary-array-variable-model',
            ),
            pytest.param(None, None, id='pass-none-variable-model'),
        ],
    )
    def test_get_playbook_variable_model(
        self, variable: str | None, expected: dict[str, Any] | None
    ) -> None:
        """Test the get_playbook_variable_model method with various variable inputs.

        This test validates the parsing of playbook variables into model objects,
        ensuring proper extraction of app_type, job_id, key, and type fields.
        """
        results = self.variables.get_playbook_variable_model(variable)
        if results is not None:
            results = results.dict()
        assert results == expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param('#App:0001:binary!Binary', 'Binary', id='pass-binary-type'),
            pytest.param(
                '#App:0001:binary_array!BinaryArray', 'BinaryArray', id='pass-binary-array-type'
            ),
            pytest.param('#App:0001:string_array!String', 'String', id='pass-string-type'),
            pytest.param(
                '#App:0001:string_array!StringArray', 'StringArray', id='pass-string-array-type'
            ),
        ],
    )
    def test_get_playbook_variable_type(self, variable: str, expected: str) -> None:
        """Test the get_playbook_variable_type method with various variable inputs.

        This test validates the extraction of type information from playbook variables,
        ensuring correct identification of Binary, BinaryArray, String, and StringArray types.
        """
        result = self.variables.get_playbook_variable_type(variable)
        assert result == expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param('#App:0001:b1!Binary', True, id='pass-binary-variable'),
            pytest.param('#App:0001:ba1!BinaryArray', True, id='pass-binary-array-variable'),
            pytest.param('#App:0001:kv1!KeyValue', True, id='pass-key-value-variable'),
            pytest.param('#App:0001:kva1!KeyValueArray', True, id='pass-key-value-array-variable'),
            pytest.param('#App:0001:s1!String', True, id='pass-string-variable'),
            pytest.param('#App:0001:sa1!StringArray', True, id='pass-string-array-variable'),
            pytest.param('#App:0001:te1!TCEntity', True, id='pass-tc-entity-variable'),
            pytest.param('#App:0001:tea1!TCEntityArray', True, id='pass-tc-entity-array-variable'),
            pytest.param(
                '#App:0001:teea1!TCEnhanceEntityArray',
                True,
                id='pass-tc-enhance-entity-array-variable',
            ),
            pytest.param('#App:0001:r1!Raw', True, id='pass-raw-variable'),
            pytest.param('#App:0001:custom!Custom', True, id='pass-custom-variable'),
            pytest.param('-- Select --', False, id='fail-select-placeholder'),
            pytest.param('-- Variable Input --', False, id='fail-variable-input-placeholder'),
            pytest.param('', False, id='fail-empty-string'),
            pytest.param(None, False, id='fail-none-value'),
            pytest.param(
                r'&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}', False, id='fail-tc-variable'
            ),
        ],
    )
    def test_is_playbook_variable(self, variable: str | None, expected: bool) -> None:
        """Test the is_playbook_variable method with various input strings.

        This test validates the identification of valid playbook variables against
        invalid inputs including special selectors, empty strings, and None values.
        """
        assert self.variables.is_playbook_variable(variable) is expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param(
                r'&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}', True, id='pass-tc-text-variable'
            ),
            pytest.param(
                r'&{TC:KEYCHAIN:4dc9202e-6945-4364-aa40-4b47655046d2}',
                True,
                id='pass-tc-keychain-variable',
            ),
            pytest.param(
                r'&{TC:FILE:4dc9202e-6945-4364-aa40-4b47655046d2}', True, id='pass-tc-file-variable'
            ),
            pytest.param('', False, id='fail-empty-string'),
            pytest.param('not_a_variable', False, id='fail-invalid-string'),
            pytest.param(None, False, id='fail-none-value'),
            pytest.param('#App:0001:binary!Binary', False, id='fail-playbook-variable'),
        ],
    )
    def test_is_tc_variable(self, variable: str | None, expected: bool) -> None:
        """Test the is_tc_variable method with various input strings.

        This test validates the identification of valid TC variables (TEXT, KEYCHAIN, FILE)
        against invalid inputs including playbook variables, empty strings, and None values.
        """
        assert self.variables.is_tc_variable(variable) is expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param(
                '#App:0001:binary!Binary',
                [
                    {
                        'origin': '#',
                        'provider': 'App',
                        'id': '0001',
                        'lookup': 'binary',
                        'type': 'Binary',
                    }
                ],
                id='pass-single-binary-variable',
            ),
            pytest.param(
                '#App:0001:binary_array!BinaryArray',
                [
                    {
                        'origin': '#',
                        'provider': 'App',
                        'id': '0001',
                        'lookup': 'binary_array',
                        'type': 'BinaryArray',
                    }
                ],
                id='pass-single-binary-array-variable',
            ),
            pytest.param(
                'dummy-data#App:0001:string!Stringdummy-data',
                [
                    {
                        'origin': '#',
                        'provider': 'App',
                        'id': '0001',
                        'lookup': 'string',
                        'type': 'String',
                    }
                ],
                id='pass-embedded-string-variable',
            ),
            pytest.param(
                (
                    r'mixed variable types #App:0001:binary!Binary '
                    r'&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}'
                ),
                [
                    {
                        'origin': '#',
                        'provider': 'App',
                        'id': '0001',
                        'lookup': 'binary',
                        'type': 'Binary',
                    },
                    {
                        'origin': '&',
                        'provider': 'TC',
                        'id': 'TEXT',
                        'lookup': '4dc9202e-6945-4364-aa40-4b47655046d2',
                        'type': None,
                    },
                ],
                id='pass-mixed-variable-types',
            ),
        ],
    )
    def test_variable_expansion_pattern(
        self, variable: str, expected: list[dict[str, Any]]
    ) -> None:
        """Test the variable_expansion_pattern regex with various variable strings.

        This test validates the regex pattern that matches and extracts components
        from both playbook and TC variables in mixed-content strings.
        """
        for index, match in enumerate(
            re.finditer(self.variables.variable_expansion_pattern, str(variable))
        ):
            assert match.groupdict() == expected[index]

    def test_variable_playbook_array_types(self) -> None:
        """Test the variable_playbook_array_types property.

        This test validates that the correct number of playbook array types
        are defined in the Variable class configuration.
        """
        assert len(self.variables.variable_playbook_array_types) == 5

    # variable_playbook_match -> tested with is_playbook_variable

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param(
                '#App:0001:app.data!Binary',
                'app_data_binary',
                id='pass-app-data-binary-method-name',
            ),
            pytest.param(
                '#App:0001:app.data!BinaryArray',
                'app_data_binaryarray',
                id='pass-app-data-binary-array-method-name',
            ),
            pytest.param(
                '#App:0001:app.data!String',
                'app_data_string',
                id='pass-app-data-string-method-name',
            ),
            pytest.param(
                '#App:0001:app.data!StringArray',
                'app_data_stringarray',
                id='pass-app-data-string-array-method-name',
            ),
            pytest.param(
                '#App:0001:app.data!Custom',
                'app_data_custom',
                id='pass-app-data-custom-method-name',
            ),
        ],
    )
    def test_variable_playbook_method_name(self, variable: str, expected: str) -> None:
        """Test the variable_playbook_method_name method with various playbook variables.

        This test validates the conversion of playbook variables to method names,
        ensuring proper formatting with app data keys and type suffixes.
        """
        assert self.variables.variable_playbook_method_name(variable) == expected

    # variable_playbook_parse -> get_playbook_variable_model
    # variable_playbook_pattern -> get_playbook_variable_model (via variable_playbook_parse)

    def test_variable_playbook_single_types(self) -> None:
        """Test the variable_playbook_single_types property.

        This test validates that the correct number of playbook single types
        are defined in the Variable class configuration.
        """
        assert len(self.variables.variable_playbook_single_types) == 5

    def test_variable_playbook_types(self) -> None:
        """Test the variable_playbook_types property.

        This test validates that the correct total number of playbook types
        (both single and array types) are defined in the Variable class configuration.
        """
        assert len(self.variables.variable_playbook_types) == 10

    # variable_tc_match -> tested with is_tc_variable

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param(
                r'&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}',
                {
                    'provider': 'TC',
                    'type': 'TEXT',
                    'key': '4dc9202e-6945-4364-aa40-4b47655046d2',
                },
                id='pass-tc-text-variable-parse',
            ),
        ],
    )
    def test_variable_tc_parse(self, variable: str, expected: dict[str, Any]) -> None:
        """Test the variable_tc_parse regex with TC variable strings.

        This test validates the regex pattern that matches and extracts provider,
        type, and key components from TC variable strings.
        """
        for match in re.finditer(self.variables.variable_tc_parse, str(variable)):
            assert match.groupdict() == expected

    # variable_tc_pattern -> tested with is_tc_variable (via variable_tc_match)
