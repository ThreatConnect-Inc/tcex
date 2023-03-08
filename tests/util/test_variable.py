"""Test Suite"""
# standard library
import re

# third-party
import pytest

# first-party
from tcex.util.variable import Variable


class TestVariable:
    """Test Suite"""

    variables = Variable()

    @pytest.mark.parametrize(
        'variable,expected',
        [
            (
                '#App:0001:binary!Binary',
                {'app_type': 'App', 'job_id': '0001', 'key': 'binary', 'type': 'Binary'},
            ),
            (
                '#App:0001:binary_array!BinaryArray',
                {'app_type': 'App', 'job_id': '0001', 'key': 'binary_array', 'type': 'BinaryArray'},
            ),
            (None, None),
        ],
    )
    def test_get_playbook_variable_model(self, variable: str, expected: dict):
        """Test Case"""
        results = self.variables.get_playbook_variable_model(variable)
        if results is not None:
            results = results.dict()
        assert results == expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            ('#App:0001:binary!Binary', 'Binary'),
            ('#App:0001:binary_array!BinaryArray', 'BinaryArray'),
            ('#App:0001:string_array!String', 'String'),
            ('#App:0001:string_array!StringArray', 'StringArray'),
        ],
    )
    def test_get_playbook_variable_type(self, variable: str, expected: dict):
        """Test Case"""
        result = self.variables.get_playbook_variable_type(variable)
        assert result == expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            ('#App:0001:b1!Binary', True),
            ('#App:0001:ba1!BinaryArray', True),
            ('#App:0001:kv1!KeyValue', True),
            ('#App:0001:kva1!KeyValueArray', True),
            ('#App:0001:s1!String', True),
            ('#App:0001:sa1!StringArray', True),
            ('#App:0001:te1!TCEntity', True),
            ('#App:0001:tea1!TCEntityArray', True),
            ('#App:0001:teea1!TCEnhanceEntityArray', True),
            ('#App:0001:r1!Raw', True),
            ('#App:0001:custom!Custom', True),
            ('-- Select --', False),
            ('-- Variable Input --', False),
            ('', False),
            (None, False),
            (r'&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}', False),
        ],
    )
    def test_is_playbook_variable(self, variable: str, expected: dict):
        """Test Case"""
        assert self.variables.is_playbook_variable(variable) is expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            (r'&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}', True),
            (r'&{TC:KEYCHAIN:4dc9202e-6945-4364-aa40-4b47655046d2}', True),
            (r'&{TC:FILE:4dc9202e-6945-4364-aa40-4b47655046d2}', True),
            ('', False),
            ('not_a_variable', False),
            (None, False),
            ('#App:0001:binary!Binary', False),
        ],
    )
    def test_is_tc_variable(self, variable: str, expected: dict):
        """Test Case"""
        assert self.variables.is_tc_variable(variable) is expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            (
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
            ),
            (
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
            ),
            (
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
            ),
            (
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
            ),
        ],
    )
    def test_variable_expansion_pattern(self, variable: str, expected: list[dict]):
        """Test Case"""
        for index, match in enumerate(
            re.finditer(self.variables.variable_expansion_pattern, str(variable))
        ):
            assert match.groupdict() == expected[index]

    def test_variable_playbook_array_types(self):
        """Test Case"""
        assert len(self.variables.variable_playbook_array_types) == 5

    # variable_playbook_match -> tested with is_playbook_variable

    @pytest.mark.parametrize(
        'variable,expected',
        [
            ('#App:0001:app.data!Binary', 'app_data_binary'),
            ('#App:0001:app.data!BinaryArray', 'app_data_binaryarray'),
            ('#App:0001:app.data!String', 'app_data_string'),
            ('#App:0001:app.data!StringArray', 'app_data_stringarray'),
            ('#App:0001:app.data!Custom', 'app_data_custom'),
        ],
    )
    def test_variable_playbook_method_name(self, variable: str, expected: dict):
        """Test Case"""
        assert self.variables.variable_playbook_method_name(variable) == expected

    # variable_playbook_parse -> get_playbook_variable_model
    # variable_playbook_pattern -> get_playbook_variable_model (via variable_playbook_parse)

    def test_variable_playbook_single_types(self):
        """Test Case"""
        assert len(self.variables.variable_playbook_single_types) == 5

    def test_variable_playbook_types(self):
        """Test Case"""
        assert len(self.variables.variable_playbook_types) == 10

    # variable_tc_match -> tested with is_tc_variable

    @pytest.mark.parametrize(
        'variable,expected',
        [
            (
                r'&{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}',
                {
                    'provider': 'TC',
                    'type': 'TEXT',
                    'key': '4dc9202e-6945-4364-aa40-4b47655046d2',
                },
            ),
        ],
    )
    def test_variable_tc_parse(self, variable: str, expected: dict):
        """Test Case"""
        for match in re.finditer(self.variables.variable_tc_parse, str(variable)):
            assert match.groupdict() == expected

    # variable_tc_pattern -> tested with is_tc_variable (via variable_tc_match)
