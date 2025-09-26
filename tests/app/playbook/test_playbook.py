"""TestPlaybook for TcEx App Playbook Core Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Core Module,
specifically testing core playbook functionality including variable creation, reading,
output processing, key validation, and various data type handling across different
playbook variable types and operations for the main playbook interface.

Classes:
    TestPlaybook: Test class for TcEx App Playbook Core Module functionality

TcEx Module Tested: app.playbook.playbook
"""


from collections.abc import Callable
from typing import Any


import pytest


from tests.mock_app import MockApp


class TestPlaybook:
    """TestPlaybook for TcEx App Playbook Core Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Core Module,
    covering various core playbook scenarios including variable creation, reading,
    output processing, key validation, and proper cleanup across different playbook
    variable types and data formats for the main playbook interface.
    """

    tc_playbook_out_variables: list[str] | None = None

    def setup_class(self) -> None:
        """Configure setup before all tests.

        This method is called once before all test methods in the class to initialize
        the playbook output variables list that defines the expected output structure
        for playbook testing scenarios.
        """
        self.tc_playbook_out_variables = [
            '#App:0001:b1!Binary',
            '#App:0001:b2!Binary',
            '#App:0001:b3!Binary',
            '#App:0001:b4!Binary',
            '#App:0001:ba1!BinaryArray',
            '#App:0001:ba2!BinaryArray',
            '#App:0001:ba3!BinaryArray',
            '#App:0001:ba4!BinaryArray',
            '#App:0001:kv1!KeyValue',
            '#App:0001:kv2!KeyValue',
            '#App:0001:kv3!KeyValue',
            '#App:0001:kv4!KeyValue',
            '#App:0001:kva1!KeyValueArray',
            '#App:0001:kva2!KeyValueArray',
            '#App:0001:kva3!KeyValueArray',
            '#App:0001:kva4!KeyValueArray',
            '#App:0001:s1!String',
            '#App:0001:s2!String',
            '#App:0001:s3!String',
            '#App:0001:s4!String',
            '#App:0001:sa1!StringArray',
            '#App:0001:sa2!StringArray',
            '#App:0001:sa3!StringArray',
            '#App:0001:sa4!StringArray',
            '#App:0001:te1!TCEntity',
            '#App:0001:te2!TCEntity',
            '#App:0001:te3!TCEntity',
            '#App:0001:te4!TCEntity',
            '#App:0001:tea1!TCEntityArray',
            '#App:0001:tea2!TCEntityArray',
            '#App:0001:tea3!TCEntityArray',
            '#App:0001:tea4!TCEntityArray',
            # '#App:0001:tee1!TCEnhanceEntity',
            # '#App:0001:teea1!TCEnhanceEntityArray',
            '#App:0001:r1!Raw',
            '#App:0001:dup.name!String',
            '#App:0001:dup.name!StringArray',
        ]

    def test_playbook_check_key_requested(self, playbook_app: Callable[..., MockApp]) -> None:
        """Test Playbook Check Key Requested for TcEx App Playbook Core Module.

        This test case verifies that the playbook key request checking functionality
        works correctly by testing whether a specific key is requested by downstream
        applications, ensuring proper key validation for playbook operations.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        assert playbook.check_key_requested('b1') is True

    def test_playbook_check_variable_requested(self, playbook_app: Callable[..., MockApp]) -> None:
        """Test Playbook Check Variable Requested for TcEx App Playbook Core Module.

        This test case verifies that the playbook variable request checking functionality
        works correctly by testing whether a specific variable is requested by downstream
        applications, ensuring proper variable validation for playbook operations.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        assert playbook.check_variable_requested('#App:0001:b1!Binary') is True

    @pytest.mark.parametrize(
        'output_data',
        [
            pytest.param(
                [
                    {'variable': '#App:0001:b1!Binary', 'value': b'bytes'},
                    {
                        'variable': '#App:0001:ba1!BinaryArray',
                        'value': [b'not', b'really', b'binary'],
                    },
                    {'variable': '#App:0001:kv1!KeyValue', 'value': {'key': 'one', 'value': '1'}},
                    {
                        'variable': '#App:0001:kva1!KeyValueArray',
                        'value': [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                    },
                    {'variable': '#App:0001:s1!String', 'value': '1'},
                    {'variable': '#App:0001:sa1!StringArray', 'value': ['a', 'b', 'c']},
                    {
                        'variable': '#App:0001:te1!TCEntity',
                        'value': {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                    },
                    {
                        'variable': '#App:0001:tea1!TCEntityArray',
                        'value': [
                            {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                            {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                        ],
                    },
                    {'variable': '#App:0001:r1!Raw', 'value': b'raw data'},
                    {'variable': '#App:0001:n1!None', 'value': None},
                ],
                id='pass-comprehensive-output-data',
            )
        ],
    )
    def test_playbook_output_add_all(
        self, output_data: list[dict], playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Output Add All for TcEx App Playbook Core Module.

        This test case verifies that the playbook output processing functionality
        works correctly by testing comprehensive output data including various
        data types such as binary, key-value, string, TC entity, and raw data,
        ensuring proper output creation, processing, and validation.

        Parameters:
            output_data: The comprehensive output data to test with various variable types

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        # add all output
        expected_data = {}
        for od in output_data:
            variable = od.get('variable')
            value = od.get('value')

            variable_model = tcex.util.get_playbook_variable_model(variable)
            if variable_model is None:
                pytest.fail(f'variable ({variable}) is not valid')
            playbook.output[variable_model.key] = value

            if variable in expected_data:
                if isinstance(value, list):
                    expected_data[variable].extend(value)
                else:
                    expected_data[variable].append(value)
            else:
                expected_data.setdefault(variable, value)

        # write output
        playbook.output.process()

        # validate output
        for variable, value in expected_data.items():
            result = playbook.read.variable(variable)

            assert result == value, f'result of ({result}) does not match ({value})'

            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0001:b1!Binary', b'not really binary', id='pass-binary-data'),
            pytest.param(
                '#App:0001:ba1!BinaryArray', [b'not', b'really', b'binary'], id='pass-binary-array'
            ),
            pytest.param(
                '#App:0001:kv1!KeyValue', {'key': 'one', 'value': '1'}, id='pass-keyvalue-data'
            ),
            pytest.param(
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                id='pass-keyvalue-array',
            ),
            pytest.param('#App:0001:s1!String', '1', id='pass-string-1'),
            pytest.param('#App:0001:s2!String', '2', id='pass-string-2'),
            pytest.param('#App:0001:s3!String', '3', id='pass-string-3'),
            pytest.param('#App:0001:s4!String', '4', id='pass-string-4'),
            pytest.param('#App:0001:sa1!StringArray', ['a', 'b', 'c'], id='pass-string-array'),
            pytest.param(
                '#App:0001:te1!TCEntity',
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                id='pass-tcentity',
            ),
            pytest.param(
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
                id='pass-tcentity-array',
            ),
            pytest.param('#App:0001:r1!Raw', b'raw data', id='pass-raw-data'),
            pytest.param('#App:0001:dup.name!String', 'dup name', id='pass-duplicate-name-string'),
            pytest.param(
                '#App:0001:dup.name!StringArray',
                ['dup name'],
                id='pass-duplicate-name-string-array',
            ),
        ],
    )
    def test_playbook_create_variable(
        self, variable: str, value: Any, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Create Variable for TcEx App Playbook Core Module.

        This test case verifies that the playbook variable creation functionality
        works correctly by testing various data types including binary, key-value,
        string, TC entity, and raw data, ensuring proper variable creation,
        reading, and cleanup operations.

        Parameters:
            variable: The playbook variable name to test
            value: The data value to store and retrieve

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.util.get_playbook_variable_model(variable)
        if variable_model is None:
            pytest.fail(f'variable ({variable}) is not valid')
        playbook.create.variable(variable_model.key, value, variable_model.type)
        result = playbook.read.variable(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param('#App:0001:b1!Binary', b'not really binary', id='pass-binary-data'),
            pytest.param(
                '#App:0001:ba1!BinaryArray', [b'not', b'really', b'binary'], id='pass-binary-array'
            ),
            pytest.param(
                '#App:0001:kv1!KeyValue', {'key': 'one', 'value': '1'}, id='pass-keyvalue-data'
            ),
            pytest.param(
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'one', 'value': '1'}, {'key': 'two', 'value': '2'}],
                id='pass-keyvalue-array',
            ),
            pytest.param('#App:0001:s1!String', '1', id='pass-string-1'),
            pytest.param('#App:0001:s2!String', '2', id='pass-string-2'),
            pytest.param('#App:0001:s3!String', '3', id='pass-string-3'),
            pytest.param('#App:0001:s4!String', '4', id='pass-string-4'),
            pytest.param('#App:0001:sa1!StringArray', ['a', 'b', 'c'], id='pass-string-array'),
            pytest.param(
                '#App:0001:te1!TCEntity',
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1'},
                id='pass-tcentity',
            ),
            pytest.param(
                '#App:0001:tea1!TCEntityArray',
                [
                    {'id': '001', 'type': 'Address', 'value': '1.1.1.1'},
                    {'id': '002', 'type': 'Address', 'value': '2.2.2.2'},
                ],
                id='pass-tcentity-array',
            ),
            pytest.param('#App:0001:r1!Raw', b'raw data', id='pass-raw-data'),
        ],
    )
    def test_playbook_output_variable_without_type(
        self, variable: str, value: Any, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Output Variable Without Type for TcEx App Playbook Core Module.

        This test case verifies that the playbook variable creation without explicit
        type specification works correctly by testing various data types including
        binary, key-value, string, TC entity, and raw data, ensuring proper
        automatic type detection and variable creation.

        Parameters:
            variable: The playbook variable name to test
            value: The data value to store and retrieve

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.util.get_playbook_variable_model(variable)
        if variable_model is None:
            pytest.fail(f'variable ({variable}) is not valid')

        playbook.create.variable(variable_model.key, value)
        result = playbook.read.variable(variable)
        assert result == value, f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0001:not_requested!String', 'not requested', id='pass-not-requested'
            ),
            pytest.param('#App:0001:none!String', 'None', id='pass-none-value'),
            pytest.param('#App:0001:dup.name!String', None, id='pass-duplicate-name-string'),
            pytest.param(
                '#App:0001:dup.name!StringArray', None, id='pass-duplicate-name-string-array'
            ),
        ],
    )
    def test_playbook_output_variable_not_written(
        self, variable: str, value: Any, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Output Variable Not Written for TcEx App Playbook Core Module.

        This test case verifies that the playbook variable creation properly handles
        cases where variables should not be written, including not requested variables,
        None values, and duplicate name scenarios, ensuring appropriate behavior
        for edge cases in variable creation.

        Parameters:
            variable: The playbook variable name to test
            value: The data value to test

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.util.get_playbook_variable_model(variable)
        if variable_model is None:
            pytest.fail(f'variable ({variable}) is not valid')

        playbook.create.variable(variable_model.key, value, variable_model.type)

        result = playbook.read.variable(variable)
        assert result is None, f'result of ({result}) should be None'

    @pytest.mark.parametrize(
        'variable,value',
        [
            pytest.param(
                '#App:0001:not_requested!String', 'not requested', id='pass-not-requested'
            ),
            pytest.param('#App:0001:none!String', None, id='pass-none-value'),
            pytest.param(None, None, id='pass-null-variable'),  # coverage
        ],
    )
    def test_playbook_output_variable_not_written_without_type(
        self, variable: str | None, value: str | None, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Output Variable Not Written Without Type for TcEx App Playbook Core Module.

        This test case verifies that the playbook variable creation without explicit
        type specification properly handles cases where variables should not be written,
        including not requested variables, None values, and null variable scenarios,
        ensuring appropriate behavior for edge cases in variable creation.

        Parameters:
            variable: The playbook variable name to test
            value: The data value to test

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.util.get_playbook_variable_model(variable)

        # only assert variable_model is None if provided variable is not None
        if variable is not None and variable_model is None:
            assert variable_model is not None, f'variable ({variable}) should not be None'

        if variable_model is not None:
            variable_key = None  # coverage
            variable_key = variable_model.key
            playbook.create.variable(variable_key, value)

        result = playbook.read.variable(variable)
        assert result is None, f'result of ({result}) should be None'

    # @pytest.mark.parametrize(
    #     'variable,value',
    #     [('#App:0001:s1!String', '1')],
    # )
    # def test_playbook_read_array(self, variable, value, playbook_app: Callable[..., MockApp]):
    #     """Test the create output method of Playbook module."""
    #     tcex = playbook_app(
    #         config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
    #     ).tcex
    #     playbook = tcex.app.playbook

    #     # parse variable and send to output.variable() method
    #     variable_model = tcex.util.get_playbook_variable_model(variable)
    #     playbook.create.variable(variable_model.key, value, variable_model.type)
    #     result = playbook.read_array(variable)
    #     assert result == [value], f'result of ({result}) does not match ({value})'

    #     playbook.delete.variable(variable)
    #     assert playbook.read.variable(variable) is None

    @pytest.mark.parametrize(
        'variable,value',
        [pytest.param('#App:0001:s1!String', '1', id='pass-string-value')],
    )
    def test_playbook_read(
        self, variable: str, value: str, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Read for TcEx App Playbook Core Module.

        This test case verifies that the playbook read functionality works correctly
        by testing variable reading with array parameter, ensuring proper
        variable retrieval and array conversion for playbook operations.

        Parameters:
            variable: The playbook variable name to test
            value: The data value to store and retrieve

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        # parse variable and send to output.variable() method
        variable_model = tcex.util.get_playbook_variable_model(variable)
        if variable_model is None:
            pytest.fail(f'variable ({variable}) is not valid')
        playbook.create.variable(variable_model.key, value, variable_model.type)
        result = playbook.read.variable(variable, array=True)
        assert result == [value], f'result of ({result}) does not match ({value})'

        playbook.delete.variable(variable)
        assert playbook.read.variable(variable) is None

    def test_playbook_read_none_array(self, playbook_app: Callable[..., MockApp]) -> None:
        """Test Playbook Read None Array for TcEx App Playbook Core Module.

        This test case verifies that the playbook read functionality properly handles
        None values when reading with array parameter, ensuring appropriate
        behavior for null variable scenarios in array reading operations.

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        # parse variable and send to output.variable() method
        result = playbook.read.variable('#App:0001:none!String', array=True)
        assert result == [], f'result of ({result}) does not match ([])'

    # @pytest.mark.parametrize(
    #     'variable,value,alt_variable,alt_value,expected',
    #     [
    #         ('#App:0001:s1!String', '1', '#App:0001:s2!String', '2', '1'),
    #         ('-- Select --', None, '#App:0001:s2!String', '6', None),
    #         ('-- Variable Input --', None, '#App:0001:s2!String', '7', '7'),
    #         (None, None, '#App:0001:s2!String', '8', None),
    #         ('-- Variable Input --', None, None, None, None),
    #     ],
    # )
    # def test_playbook_read_choice(
    #     self,
    #     variable,
    #     value,
    #     alt_variable,
    #     alt_value,
    #     expected,
    #     playbook_app: Callable[..., MockApp],
    # ):
    #     """Test the create output method of Playbook module."""
    #     tcex = playbook_app(
    #         config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
    #     ).tcex
    #     playbook = tcex.app.playbook

    #     # parse variable and send to output.variable() method
    #     if value is not None:
    #         variable_model = tcex.util.get_playbook_variable_model(variable)
    #         playbook.create.variable(variable_model.key, value, variable_model.type)

    #     # parse alt variable and send to output.variable() method
    #     if alt_value is not None:
    #         variable_model = tcex.util.get_playbook_variable_model(variable)
    #         playbook.output.variable(variable_model.key, alt_value, variable_model.type)

    #     # read choice
    #     result = playbook.read_choice(variable, alt_variable)
    #     assert result == expected, f'result of ({result}) does not match ({expected})'

    #     # cleanup
    #     if value is not None:
    #         playbook.delete.variable(variable)
    #         assert playbook.read.variable(variable) is None
    #     if alt_value is not None:
    #         playbook.delete.variable(alt_variable)
    #         assert playbook.read.variable(alt_variable) is None
