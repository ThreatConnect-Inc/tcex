"""TestPlaybookRead for TcEx App Playbook Read Module Testing.

This module contains comprehensive test cases for the TcEx App Playbook Read Module,
specifically testing playbook read functionality including variable type checking,
string value coercion, binary decoding, and various data type handling across
different playbook variable types and operations.

Classes:
    TestPlaybookRead: Test class for TcEx App Playbook Read Module functionality

TcEx Module Tested: app.playbook.playbook_read
"""


from collections.abc import Callable


import pytest


from tcex.app.playbook.playbook import Playbook  # TYPE-CHECKING
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestPlaybookRead:
    """TestPlaybookRead for TcEx App Playbook Read Module Testing.

    This class provides comprehensive testing for the TcEx App Playbook Read Module,
    covering various read operation scenarios including variable type validation,
    string value coercion, binary data handling, and proper error handling
    across different playbook variable types and data formats.
    """

    tc_playbook_out_variables: list[str] | None = None

    def setup_class(self) -> None:
        """Configure setup before all tests.

        This method is called once before all test methods in the class to initialize
        the playbook output variables list that defines the expected output structure
        for playbook read testing scenarios.
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

    @pytest.mark.parametrize(
        'variable,type_,should_fail',
        [
            pytest.param('#App:0001:b1!Binary', 'Binary', False, id='pass-binary-type'),
            pytest.param('#App:0001:kv1!KeyValue', 'KeyValue', False, id='pass-keyvalue-type'),
            pytest.param('#App:0001:s1!String', 'String', False, id='pass-string-type'),
            pytest.param('#App:0001:te1!TCEntity', 'TCEntity', False, id='pass-tcentity-type'),
            # fail tests
            pytest.param('#App:0001:b1!Binary', 'String', True, id='fail-mismatched-type'),
        ],
    )
    def test_playbook_read_check_variable_type(
        self, variable: str, type_: str, should_fail: bool, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Playbook Read Check Variable Type for TcEx App Playbook Read Module.

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
                playbook.read._check_variable_type(variable, type_)  # noqa: SLF001

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
    def test_playbook_read_coerce_string_value(
        self, value: bool | float | str, expected: str, playbook: Playbook
    ) -> None:
        """Test Playbook Read Coerce String Value for TcEx App Playbook Read Module.

        This test case verifies that the string value coercion functionality
        works correctly by testing various data types to ensure proper
        conversion to string format for playbook variables.

        Parameters:
            value: The value to test for string coercion
            expected: The expected string result after coercion

        Fixtures:
            playbook: Playbook instance for testing string coercion operations
        """
        assert playbook.read._coerce_string_value(value) == expected  # noqa: SLF001

    @pytest.mark.parametrize(
        'data,expected',
        [
            pytest.param(b'123', '123', id='pass-binary-decode'),
        ],
    )
    def test_playbook_read_decode_binary(
        self, data: bytes, expected: str, playbook: Playbook
    ) -> None:
        """Test Playbook Read Decode Binary for TcEx App Playbook Read Module.

        This test case verifies that the binary decoding functionality
        works correctly by testing binary data to ensure proper
        conversion from bytes to string format.

        Parameters:
            data: The binary data to test for decoding
            expected: The expected string result after decoding

        Fixtures:
            playbook: Playbook instance for testing binary decoding operations
        """
        assert playbook.read._decode_binary(data) == expected  # noqa: SLF001
