"""TestPlaybookCreate for TcEx App Playbook Create Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Create Module,
specifically testing playbook variable creation functionality including null checking,
request validation, variable type validation, data coercion, and various data type
creation methods across different playbook variable types and scenarios.

Classes:
    TestPlaybookCreate: Test class for TcEx App Playbook Create Module functionality

TcEx Module Tested: app.playbook.playbook_create
"""


from collections.abc import Callable
from typing import Any


import pytest


from tcex.input.field_type import KeyValue
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestPlaybookCreate:
    """TestPlaybookCreate for TcEx App Playbook Create Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Create Module,
    covering various playbook variable creation scenarios including utility methods,
    data validation, type checking, and creation methods for all supported data
    types including binary, string, key-value, and TC entity variables.
    """

    tc_playbook_out_variables: list[str] | None = None

    def setup_class(self) -> None:
        """Configure setup before all tests.

        This method is called once before all test methods in the class to initialize
        the playbook output variables list that defines the expected output structure
        for playbook create testing scenarios.
        """
        self.tc_playbook_out_variables = [
            '#App:0001:b1!Binary',
            '#App:0001:ba1!BinaryArray',
            '#App:0001:kv1!KeyValue',
            '#App:0001:kva1!KeyValueArray',
            '#App:0001:s1!String',
            '#App:0001:sa1!StringArray',
            '#App:0001:te1!TCEntity',
            '#App:0001:tea1!TCEntityArray',
            # '#App:0001:tee1!TCEnhanceEntity',
            '#App:0001:r1!Raw',
        ]

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method is called before each test method to reset scoped and cached
        properties, ensuring a clean testing environment for each test case.
        """
        scoped_property._reset()  # noqa: SLF001
        cached_property._reset()  # noqa: SLF001

    @pytest.mark.parametrize(
        'key,value,expected',
        [
            pytest.param('ba1', b'bytes 1', False, id='pass-valid-key-value'),
            pytest.param('#App:0002:b1!Binary', b'bytes 1', False, id='pass-full-variable'),
            pytest.param(None, b'bytes 2', True, id='fail-null-key'),
            pytest.param('#App:0002:b3!Binary', None, True, id='fail-null-value'),
        ],
    )
    def test_playbook_create_check_null(
        self, key: str, value: bytes, expected: bool, playbook
    ) -> None:
        """Test Playbook Create Check Null for TcEx App Playbook Create Module.

        This test case verifies that the null checking functionality works correctly
        by testing various key and value combinations to ensure proper null
        detection and validation.

        Parameters:
            key: The key to test for null validation
            value: The value to test for null validation
            expected: The expected boolean result of the null check

        Fixtures:
            playbook: Playbook instance for testing null check operations
        """
        assert playbook.create._check_null(key, value) is expected  # noqa: SLF001

    @pytest.mark.parametrize(
        'variable,when_requested,expected',
        [
            pytest.param('#App:0001:b1!Binary', True, True, id='pass-binary-requested'),
            pytest.param('#App:0001:kv1!KeyValue', True, True, id='pass-keyvalue-requested'),
            pytest.param('#App:0001:s1!String', True, True, id='pass-string-requested'),
            pytest.param('#App:0001:te1!TCEntity', True, True, id='pass-tcentity-requested'),
            pytest.param(
                '#App:0001:app.force.create!TCEntity', False, True, id='pass-force-create'
            ),
            pytest.param('not_a_variable', True, False, id='fail-not-variable'),
            pytest.param('#App:0001:not.requested!TCEntity', True, False, id='fail-not-requested'),
        ],
    )
    def test_playbook_create_check_requested(
        self,
        variable: str,
        expected: bool,
        when_requested: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create Check Requested for TcEx App Playbook Create Module.

        This test case verifies that the requested variable checking functionality
        works correctly by testing various variable formats and request states
        to ensure proper validation of downstream app requests.

        Parameters:
            variable: The variable string to test for request validation
            expected: The expected boolean result of the request check
            when_requested: Whether to check if the variable was requested

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        assert playbook.create._check_requested(variable, when_requested) is expected  # noqa: SLF001

    @pytest.mark.parametrize(
        'variable,type_,should_fail',
        [
            pytest.param('#App:0001:b1!Binary', 'Binary', False, id='pass-binary-type'),
            pytest.param('#App:0001:kv1!KeyValue', 'KeyValue', False, id='pass-keyvalue-type'),
            pytest.param('#App:0001:s1!String', 'String', False, id='pass-string-type'),
            pytest.param('#App:0001:te1!TCEntity', 'TCEntity', False, id='pass-tcentity-type'),
            pytest.param('#App:0001:b1!Binary', 'String', True, id='fail-mismatched-type'),
        ],
    )
    def test_playbook_create_check_variable_type(
        self, variable: str, type_: str, should_fail: bool, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Create Check Variable Type for TcEx App Playbook Create Module.

        This test case verifies that the variable type checking functionality
        works correctly by testing various variable and type combinations
        to ensure proper type validation and error handling.

        Parameters:
            variable: The variable string to test for type validation
            type_: The expected type to validate against
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        if should_fail is False:
            assert True
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create._check_variable_type(variable, type_)  # noqa: SLF001

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'value,expected',
        [
            pytest.param(True, 'true', id='pass-boolean-true'),
            pytest.param(1.1, '1.1', id='pass-float'),
            pytest.param(1, '1', id='pass-integer'),
            pytest.param('string', 'string', id='pass-string'),
            pytest.param(None, None, id='pass-none'),
        ],
    )
    def test_playbook_create_coerce_string_value(
        self, value: bool | float | str, expected: str, playbook
    ) -> None:
        """Test Playbook Create Coerce String Value for TcEx App Playbook Create Module.

        This test case verifies that the string value coercion functionality
        works correctly by testing various data types to ensure proper
        conversion to string format for playbook variables.

        Parameters:
            value: The value to test for string coercion
            expected: The expected string result after coercion

        Fixtures:
            playbook: Playbook instance for testing string coercion operations
        """
        assert playbook.create._coerce_string_value(value) == expected  # noqa: SLF001

    @pytest.mark.parametrize(
        'variable,variable_type,expected',
        [
            pytest.param(
                '#App:0001:b1!Binary',
                None,
                '#App:0001:b1!Binary',
                id='pass-full-variable'
            ),
            pytest.param('kv1', None, '#App:0001:kv1!KeyValue', id='pass-short-key'),
            pytest.param('kv1', 'KeyValue', '#App:0001:kv1!KeyValue', id='pass-key-with-type'),
            pytest.param('unknown', None, None, id='fail-unknown-key'),
            pytest.param('unknown', 'KeyValue', None, id='fail-unknown-key-with-type'),
        ],
    )
    def test_playbook_create_get_variable(
        self,
        variable: str,
        variable_type: str | None,
        expected: str,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create Get Variable for TcEx App Playbook Create Module.

        This test case verifies that the variable resolution functionality works
        correctly by testing various key formats and type specifications to
        ensure proper variable name construction and validation.

        Parameters:
            variable: The variable key or name to resolve
            variable_type: The optional variable type specification
            expected: The expected resolved variable name

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        assert playbook.create._get_variable(variable, variable_type) == expected  # noqa: SLF001

    # TODO: [lowest] add test for _serialize_data
    # def test_playbook_create_serialize_data()

    @pytest.mark.parametrize(
        'value,validate,allow_none,expected,should_fail',
        [
            pytest.param(
                {'key': 'key', 'value': 'value'},
                True,
                False,
                {'key': 'key', 'value': 'value'},
                False,
                id='pass-dict-keyvalue'
            ),
            pytest.param(
                KeyValue(key='key', value='value'),  # type: ignore
                True,
                False,
                {'key': 'key', 'value': 'value'},
                False,
                id='pass-keyvalue-object'
            ),
            pytest.param(None, True, False, None, True, id='fail-none-not-allowed'),
        ],
    )
    def test_playbook_create_process_object_types(
        self,
        value: KeyValue | dict,
        validate: bool,
        allow_none: bool,
        expected: str,
        should_fail: bool,
        playbook,
    ) -> None:
        """Test Playbook Create Process Object Types for TcEx App Playbook Create Module.

        This test case verifies that the object type processing functionality
        works correctly by testing various object types and validation settings
        to ensure proper object handling and error conditions.

        Parameters:
            value: The object value to process
            validate: Whether to perform validation
            allow_none: Whether to allow None values
            expected: The expected processed result
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook: Playbook instance for testing object type processing operations
        """
        if should_fail is False:
            assert playbook.create._process_object_types(value, validate, allow_none) == expected  # noqa: SLF001
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create._process_object_types(value, validate, allow_none)  # noqa: SLF001

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'data,expected',
        [
            pytest.param({'key': 'key', 'value': 'value'}, True, id='pass-valid-keyvalue'),
            pytest.param(
                {'key1': 'key', 'value2': 'value'}, False, id='fail-invalid-keyvalue-keys'
            ),
            pytest.param('string', False, id='fail-not-dict'),
        ],
    )
    def test_playbook_create_is_key_value(
        self,
        data: dict,
        expected: bool,
        playbook,
    ) -> None:
        """Test Playbook Create Is Key Value for TcEx App Playbook Create Module.

        This test case verifies that the key-value validation functionality
        works correctly by testing various data structures to ensure proper
        identification of valid key-value pairs.

        Parameters:
            data: The data structure to test for key-value validation
            expected: The expected boolean result of the validation

        Fixtures:
            playbook: Playbook instance for testing key-value validation operations
        """
        assert playbook.create.is_key_value(data) == expected

    @pytest.mark.parametrize(
        'variable,expected',
        [
            pytest.param('#App:0001:b1!Binary', True, id='pass-binary-requested'),
            pytest.param('#App:0001:kv1!KeyValue', True, id='pass-keyvalue-requested'),
            pytest.param('kv1', False, id='fail-short-key'),
            pytest.param(None, False, id='fail-none-key'),
        ],
    )
    def test_playbook_create_is_requested(
        self, variable: str, expected: bool, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Create Is Requested for TcEx App Playbook Create Module.

        This test case verifies that the requested variable checking functionality
        works correctly by testing various variable formats to ensure proper
        identification of requested output variables.

        Parameters:
            variable: The variable string to test for request validation
            expected: The expected boolean result of the request check

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        assert playbook.create.is_requested(variable) is expected

    @pytest.mark.parametrize(
        'data,expected',
        [
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'}, True, id='pass-valid-tcentity'
            ),
            pytest.param({'type': 'Address', 'value': '1.1.1.1'}, False, id='fail-missing-id'),
            pytest.param('string', False, id='fail-not-dict'),
        ],
    )
    def test_playbook_create_is_tc_entity(
        self,
        data: dict,
        expected: bool,
        playbook,
    ) -> None:
        """Test Playbook Create Is TC Entity for TcEx App Playbook Create Module.

        This test case verifies that the TC entity validation functionality
        works correctly by testing various data structures to ensure proper
        identification of valid TC entity objects.

        Parameters:
            data: The data structure to test for TC entity validation
            expected: The expected boolean result of the validation

        Fixtures:
            playbook: Playbook instance for testing TC entity validation operations
        """
        assert playbook.create.is_tc_entity(data) == expected

    @pytest.mark.parametrize(
        'key,value,validate,variable_type,when_requested,expected',
        [
            pytest.param(None, b'123', True, None, True, None, id='fail-null-key'),
            pytest.param('b1', b'123', True, None, True, b'123', id='pass-binary-default'),
            pytest.param('b1', b'123', True, 'Binary', True, b'123', id='pass-binary-with-type'),
            pytest.param(
                '#App:0001:not-requested!Binary',
                b'123',
                True,
                None,
                True,
                None,
                id='fail-not-requested',
            ),
            pytest.param(
                '#App:0001:not-requested!Binary',
                b'123',
                True,
                None,
                False,
                b'123',
                id='pass-force-create',
            ),
            pytest.param(
                '#App:0001:b1!Binary', b'123', True, None, True, b'123', id='pass-full-variable'
            ),
        ],
    )
    def test_playbook_create_any(
        self,
        key: str,
        value: Any,
        validate: bool,
        variable_type: str,
        when_requested: bool,
        expected: Any,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create Any for TcEx App Playbook Create Module.

        This test case verifies that the generic creation functionality works
        correctly by testing various key formats, validation settings, and
        request states to ensure proper variable creation across all types.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            variable_type: The optional variable type specification
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook

        playbook.create.any(key, value, validate, variable_type, when_requested)
        variable = playbook.create._get_variable(key, variable_type)  # noqa: SLF001
        assert playbook.read.variable(variable) == expected

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            pytest.param(None, b'123', True, True, None, False, id='pass-null-key'),
            pytest.param('b1', b'123', True, True, b'123', False, id='pass-valid-binary'),
            pytest.param(
                '#App:0001:not-requested!Binary',
                b'123',
                True,
                True,
                None,
                False,
                id='pass-not-requested'
            ),
            pytest.param(
                '#App:0001:not-requested!Binary',
                b'123',
                True,
                False,
                b'123',
                False,
                id='pass-force-create'
            ),
            pytest.param(
                '#App:0001:b1!Binary',
                b'123',
                True,
                True,
                b'123',
                False,
                id='pass-full-variable'
            ),
            pytest.param(
                '#App:0001:b1!Binary',
                'not binary 1',
                True,
                True,
                None,
                True,
                id='fail-invalid-type'
            ),
            pytest.param(
                '#App:0001:b1!Binary', [], True, True, None, True, id='fail-list-type'
            ),
            pytest.param(
                '#App:0001:b1!Binary', {}, True, True, None, True, id='fail-dict-type'
            ),
            pytest.param(
                '#App:0001:s1!String',
                'wrong type',
                True,
                True,
                None,
                True,
                id='fail-wrong-variable-type'
            ),
        ],
    )
    def test_playbook_create_binary_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create Binary Method for TcEx App Playbook Create Module.

        This test case verifies that the binary variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper binary variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'Binary')  # noqa: SLF001

        if should_fail is False:
            playbook.create.binary(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.binary(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            pytest.param(None, [b'123'], True, True, None, False, id='pass-null-key'),
            pytest.param(
                'ba1',
                [b'123'],
                True,
                True,
                [b'123'],
                False,
                id='pass-valid-binary-array'
            ),
            pytest.param(
                '#App:0001:not-requested!BinaryArray',
                [b'123'],
                True,
                True,
                None,
                False,
                id='pass-not-requested'
            ),
            pytest.param(
                '#App:0001:not-requested!BinaryArray',
                [b'123'],
                True,
                False,
                [b'123'],
                False,
                id='pass-force-create'
            ),
            pytest.param(
                '#App:0001:ba1!BinaryArray',
                [b'123'],
                True,
                True,
                [b'123'],
                False,
                id='pass-full-variable'
            ),
            pytest.param(
                '#App:0001:ba1!BinaryArray',
                'not binary 1',
                True,
                True,
                None,
                True,
                id='fail-invalid-type'
            ),
            pytest.param(
                '#App:0001:ba1!BinaryArray',
                [b'123', 'abc'],
                True,
                True,
                None,
                True,
                id='fail-mixed-types'
            ),
            pytest.param(
                '#App:0001:ba1!BinaryArray', {}, True, True, None, True, id='fail-dict-type'
            ),
            pytest.param(
                '#App:0001:s1!String',
                'wrong type',
                True,
                True,
                None,
                True,
                id='fail-wrong-variable-type'
            ),
        ],
    )
    def test_playbook_create_binary_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create Binary Array Method for TcEx App Playbook Create Module.

        This test case verifies that the binary array variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper binary array variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'BinaryArray')  # noqa: SLF001

        if should_fail is False:
            playbook.create.binary_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.binary_array(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            pytest.param(
                None, {'key': 'key', 'value': 'value'}, True, True, None, False, id='pass-null-key'
            ),
            pytest.param(
                'kv1',
                {'key': 'key', 'value': 'value'},
                True,
                True,
                {'key': 'key', 'value': 'value'},
                False,
                id='pass-valid-keyvalue',
            ),
            pytest.param(
                '#App:0001:not-requested!KeyValue',
                {'key': 'key', 'value': 'value'},
                True,
                True,
                None,
                False,
                id='pass-not-requested',
            ),
            pytest.param(
                '#App:0001:not-requested!KeyValue',
                {'key': 'key', 'value': 'value'},
                True,
                False,
                {'key': 'key', 'value': 'value'},
                False,
                id='pass-force-create',
            ),
            pytest.param(
                '#App:0001:kv1!KeyValue',
                {'key': 'key', 'value': 'value'},
                True,
                True,
                {'key': 'key', 'value': 'value'},
                False,
                id='pass-full-variable',
            ),
            pytest.param(
                '#App:0001:kv1!KeyValue',
                'not key value 1',
                True,
                True,
                None,
                True,
                id='fail-invalid-type',
            ),
            pytest.param('#App:0001:kv1!KeyValue', [], True, True, None, True, id='fail-list-type'),
            pytest.param(
                '#App:0001:kv1!KeyValue', {}, True, True, None, True, id='fail-empty-dict'
            ),
            pytest.param(
                '#App:0001:s1!String',
                'wrong type',
                True,
                True,
                None,
                True,
                id='fail-wrong-variable-type',
            ),
        ],
    )
    def test_playbook_create_key_value_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create Key Value Method for TcEx App Playbook Create Module.

        This test case verifies that the key-value variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper key-value variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'KeyValue')  # noqa: SLF001

        if should_fail is False:
            playbook.create.key_value(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.key_value(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            pytest.param(
                None,
                [{'key': 'key', 'value': 'value'}],
                True,
                True,
                None,
                False,
                id='pass-null-key',
            ),
            pytest.param(
                'kva1',
                [{'key': 'key', 'value': 'value'}],
                True,
                True,
                [{'key': 'key', 'value': 'value'}],
                False,
                id='pass-valid-keyvalue-array',
            ),
            pytest.param(
                '#App:0001:not-requested!KeyValueArray',
                [{'key': 'key', 'value': 'value'}],
                True,
                True,
                None,
                False,
                id='pass-not-requested',
            ),
            pytest.param(
                '#App:0001:not-requested!KeyValueArray',
                [{'key': 'key', 'value': 'value'}],
                True,
                False,
                [{'key': 'key', 'value': 'value'}],
                False,
                id='pass-force-create',
            ),
            pytest.param(
                '#App:0001:kva1!KeyValueArray',
                [{'key': 'key', 'value': 'value'}],
                True,
                True,
                [{'key': 'key', 'value': 'value'}],
                False,
                id='pass-full-variable',
            ),
            pytest.param(
                '#App:0001:kva1!KeyValueArray',
                'not key value array 1',
                True,
                True,
                None,
                True,
                id='fail-invalid-type',
            ),
            pytest.param(
                '#App:0001:kva1!KeyValueArray', [], True, True, None, True, id='fail-empty-array'
            ),
            pytest.param(
                '#App:0001:kva1!KeyValueArray', {}, True, True, None, True, id='fail-dict-type'
            ),
            pytest.param(
                '#App:0001:s1!String',
                'wrong type',
                True,
                True,
                None,
                True,
                id='fail-wrong-variable-type',
            ),
        ],
    )
    def test_playbook_create_key_value_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create Key Value Array Method for TcEx App Playbook Create Module.

        This test case verifies that the key-value array variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper key-value array variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'KeyValueArray')  # noqa: SLF001

        if should_fail is False:
            playbook.create.key_value_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.key_value(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            pytest.param(None, 'string', True, True, None, False, id='pass-null-key'),
            pytest.param('s1', 'string', True, True, 'string', False, id='pass-valid-string'),
            pytest.param(
                '#App:0001:not-requested!String',
                'string',
                True,
                True,
                None,
                False,
                id='pass-not-requested',
            ),
            pytest.param(
                '#App:0001:not-requested!String',
                'string',
                True,
                False,
                'string',
                False,
                id='pass-force-create',
            ),
            pytest.param(
                '#App:0001:s1!String',
                'string',
                True,
                True,
                'string',
                False,
                id='pass-full-variable',
            ),
            pytest.param(
                '#App:0001:s1!String', b'not String 1', True, True, None, True, id='fail-bytes-type'
            ),
            pytest.param('#App:0001:s1!String', [], True, True, None, True, id='fail-list-type'),
            pytest.param('#App:0001:s1!String', {}, True, True, None, True, id='fail-dict-type'),
            pytest.param(
                '#App:0001:b1!Binary',
                b'wrong type',
                True,
                True,
                None,
                True,
                id='fail-wrong-variable-type',
            ),
        ],
    )
    def test_playbook_create_string_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create String Method for TcEx App Playbook Create Module.

        This test case verifies that the string variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper string variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'String')  # noqa: SLF001

        if should_fail is False:
            playbook.create.string(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.string(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            pytest.param(None, ['string'], True, True, None, False, id='pass-null-key'),
            pytest.param(
                'sa1', ['string'], True, True, ['string'], False, id='pass-valid-string-array'
            ),
            pytest.param(
                '#App:0001:not-requested!StringArray',
                ['string'],
                True,
                True,
                None,
                False,
                id='pass-not-requested',
            ),
            pytest.param(
                '#App:0001:not-requested!StringArray',
                ['string'],
                True,
                False,
                ['string'],
                False,
                id='pass-force-create',
            ),
            pytest.param(
                '#App:0001:sa1!StringArray',
                ['string'],
                True,
                True,
                ['string'],
                False,
                id='pass-full-variable',
            ),
            pytest.param(
                '#App:0001:sa1!StringArray',
                'not string array 1',
                True,
                True,
                None,
                True,
                id='fail-string-type',
            ),
            pytest.param(
                '#App:0001:sa1!StringArray',
                ['string', b'abc'],
                True,
                True,
                None,
                True,
                id='fail-mixed-types',
            ),
            pytest.param(
                '#App:0001:sa1!StringArray', {}, True, True, None, True, id='fail-dict-type'
            ),
            pytest.param(
                '#App:0001:b1!Binary',
                b'wrong type',
                True,
                True,
                None,
                True,
                id='fail-wrong-variable-type',
            ),
        ],
    )
    def test_playbook_create_string_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create String Array Method for TcEx App Playbook Create Module.

        This test case verifies that the string array variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper string array variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'StringArray')  # noqa: SLF001

        if should_fail is False:
            playbook.create.string_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.string_array(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            # _check_null
            (None, {'id': 123, 'type': 'Address', 'value': '1.1.1.1'}, True, True, None, False),
            # _get_variable
            (
                'te1',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                True,
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                False,
            ),
            # when requested_check=True (return None)
            (
                '#App:0001:not-requested!TCEntity',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                True,
                None,
                False,
            ),
            # when requested_check=False (force write)
            (
                '#App:0001:not-requested!TCEntity',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                False,
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                False,
            ),
            # using full variable as key
            (
                '#App:0001:te1!TCEntity',
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                True,
                True,
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                False,
            ),
            # fail tests
            ('#App:0001:te1!TCEntity', 'not key value 1', True, True, None, True),
            ('#App:0001:te1!TCEntity', [], True, True, None, True),
            ('#App:0001:te1!TCEntity', {}, True, True, None, True),
            # when_requested=False, to allow type check to hit
            ('#App:0001:s1!String', 'wrong type', True, True, None, True),
        ],
    )
    def test_playbook_create_tc_entity_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create TC Entity Method for TcEx App Playbook Create Module.

        This test case verifies that the TC entity variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper TC entity variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'TCEntity')  # noqa: SLF001

        if should_fail is False:
            playbook.create.tc_entity(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.tc_entity(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)

    @pytest.mark.parametrize(
        'key,value,validate,when_requested,expected,should_fail',
        [
            pytest.param(
                None,
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                True,
                None,
                False,
                id='pass-null-key',
            ),
            pytest.param(
                'tea1',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                True,
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                False,
                id='pass-valid-tcentity-array',
            ),
            pytest.param(
                '#App:0001:not-requested!TCEntityArray',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                True,
                None,
                False,
                id='pass-not-requested',
            ),
            pytest.param(
                '#App:0001:not-requested!TCEntityArray',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                False,
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                False,
                id='pass-force-create',
            ),
            pytest.param(
                '#App:0001:tea1!TCEntityArray',
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                True,
                True,
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                False,
                id='pass-full-variable',
            ),
            pytest.param(
                '#App:0001:tea1!TCEntityArray',
                'not tc entity array 1',
                True,
                True,
                None,
                True,
                id='fail-invalid-type',
            ),
            pytest.param(
                '#App:0001:tea1!TCEntityArray',
                ['not tc entity'],
                True,
                True,
                None,
                True,
                id='fail-invalid-entity',
            ),
            pytest.param(
                '#App:0001:tea1!TCEntityArray', {}, True, True, None, True, id='fail-dict-type'
            ),
            pytest.param(
                '#App:0001:s1!String',
                'wrong type',
                True,
                True,
                None,
                True,
                id='fail-wrong-variable-type',
            ),
        ],
    )
    def test_playbook_create_tc_entity_array_method(
        self,
        key: str,
        value: Any,
        validate: bool,
        when_requested: bool,
        expected: bool,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Playbook Create TC Entity Array Method for TcEx App Playbook Create Module.

        This test case verifies that the TC entity array variable creation functionality
        works correctly by testing various key formats, validation settings,
        and data types to ensure proper TC entity array variable creation and error handling.

        Parameters:
            key: The key or variable name to create
            value: The value to store in the variable
            validate: Whether to perform validation
            when_requested: Whether to check if the variable was requested
            expected: The expected result after creation
            should_fail: Whether the test should expect a failure

        Fixtures:
            playbook_app: Callable function that returns a configured MockApp instance
        """
        tcex = playbook_app(
            config_data={'tc_playbook_out_variables': self.tc_playbook_out_variables}
        ).tcex
        playbook = tcex.app.playbook
        # get full variable name if required
        variable = playbook.create._get_variable(key, 'TCEntityArray')  # noqa: SLF001

        if should_fail is False:
            playbook.create.tc_entity_array(key, value, validate, when_requested)
            assert playbook.read.variable(variable) == expected

            # cleanup
            playbook.delete.variable(variable)
            assert playbook.read.variable(variable) is None
        else:
            with pytest.raises(RuntimeError) as ex:
                playbook.create.tc_entity_array(key, value, validate, when_requested)

            assert 'Invalid' in str(ex.value)
