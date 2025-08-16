"""TestInputsIpAddressFieldTypes for IP Address field type validation.

This module contains comprehensive test cases for the IP Address field type functionality
within the TcEx Framework, including validation of single values, arrays, and complex
union types with entity support.

Classes:
    TestInputsIpAddressFieldTypes: Test cases for IP Address field type validation

TcEx Module Tested: tcex.input.field_type.ip_address
"""

# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel, field_validator

# first-party
from tcex.input.field_type import (AddressEntity, IpAddress, always_array,
                                   entity_input, ip_address)
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsIpAddressFieldTypes(InputTest):
    """TestInputsIpAddressFieldTypes for IP Address field type validation.

    This class provides comprehensive test coverage for IP Address field types including
    validation of single IP addresses, arrays, custom validation options, and complex
    union types with entity support.

    Fixtures:
        playbook_app: MockApp instance for testing field validation
    """

    def setup_method(self) -> None:
        """Configure setup before all tests."""
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param('1.1.1.1', '1.1.1.1', False, False, id='pass-required-valid-ipv4'),
            # optional, null input
            pytest.param(None, None, True, False, id='pass-optional-null-input'),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(None, None, False, True, id='fail-required-null-input'),
            # required, invalid IP
            pytest.param('not-an-ip', None, False, True, id='fail-required-invalid-ip'),
        ],
    )
    def test_field_model_ip_address_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test IP Address field type validation with single values.

        This test validates the IpAddress field type with various input scenarios including
        valid IP addresses, null values, and invalid inputs for both required and optional fields.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: IpAddress

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: IpAddress | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        ('input_value,expected,strip_port,optional,fail_test'),
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param(
                '1.1.1.1', '1.1.1.1', False, False, False, id='pass-required-valid-ip-no-port'
            ),
            # required, ip with port input
            pytest.param(
                '1.1.1.1:443',
                '1.1.1.1',
                True,
                False,
                False,
                id='pass-required-ip-with-port-stripped',
            ),
            # optional, null input
            pytest.param(None, None, False, True, False, id='pass-optional-null-input'),
            #
            # Fail Testing
            #
            # required, ip with port input
            pytest.param(
                '1.1.1.1:443',
                None,
                False,
                False,
                True,
                id='fail-required-ip-with-port-not-stripped',
            ),
        ],
    )
    def test_field_model_ip_address_custom_input(
        self,
        input_value: str,
        expected: str,
        strip_port: bool,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test IP Address field type with custom strip_port validation.

        This test validates the custom ip_address field type with strip_port option,
        testing scenarios where port numbers should be stripped from IP addresses.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: ip_address(strip_port=strip_port)  # type: ignore

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: ip_address(strip_port=strip_port) | None  # type: ignore

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param(['1.1.1.1'], ['1.1.1.1'], False, False, id='pass-required-valid-ip-array'),
            # required, empty input
            pytest.param([], [], False, False, id='pass-required-empty-array'),
            # optional, empty input
            pytest.param([], [], True, False, id='pass-optional-empty-array'),
            # optional, null input
            pytest.param(None, None, True, False, id='pass-optional-null-input'),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(None, None, False, True, id='fail-required-null-input'),
        ],
    )
    def test_field_model_ip_address_array_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test IP Address field type with array validation.

        This test validates the IpAddress field type in array format, testing scenarios
        with valid IP address arrays, empty arrays, and null values.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: list[IpAddress]

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: list[IpAddress] | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='StringArray',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        'input_value,expected,input_type,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, string input
            pytest.param(
                '1.1.1.1', ['1.1.1.1'], 'String', False, False, id='pass-required-string-ipv4'
            ),
            # required, string input
            pytest.param(
                '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
                ['2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
                'String',
                False,
                False,
                id='pass-required-string-ipv6',
            ),
            # required, array input
            pytest.param(
                ['1.1.1.1'], ['1.1.1.1'], 'StringArray', False, False, id='pass-required-array-ipv4'
            ),
            # required, tcentity
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                ['1.1.1.1'],
                'TCEntity',
                False,
                False,
                id='pass-required-tcentity-address',
            ),
            # required, tcentity array
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                ['1.1.1.1'],
                'TCEntityArray',
                False,
                False,
                id='pass-required-tcentity-array-address',
            ),
            #
            # Fail Testing
            #
            # required, tcentity
            pytest.param(
                {'id': 123, 'type': 'Host', 'value': 'bad.com'},
                None,
                'TCEntity',
                False,
                True,
                id='fail-required-tcentity-host-type',
            ),
            # required, null input
            pytest.param(None, None, 'String', False, True, id='fail-required-null-string'),
            # required, empty array input
            pytest.param([], [], 'StringArray', False, True, id='fail-required-empty-array'),
            # optional, empty array input
            pytest.param([], [], 'StringArray', True, True, id='fail-optional-empty-array'),
            # optional, empty string input
            pytest.param('', [], 'String', True, True, id='fail-optional-empty-string'),
            # optional, null input
            pytest.param(None, [], 'String', True, True, id='fail-optional-null-string'),
        ],
    )
    def test_field_model_ip_address_union_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test IP Address field type with union type and entity validation.

        This test validates complex union types combining IpAddress fields with AddressEntity
        types, including support for TCEntity inputs and always_array validation.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: (
                list[IpAddress] | IpAddress | list[AddressEntity] | AddressEntity  # type: ignore
            )

            _entity_input = field_validator('my_data')(
                entity_input(only_field='value')  # type: ignore
            )
            _always_array = field_validator('my_data')(always_array(allow_empty=False))

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: None | (
                list[IpAddress]
                | IpAddress
                | list[AddressEntity]  # type: ignore
                | AddressEntity  # type: ignore
            )

            _entity_input = field_validator('my_data')(
                entity_input(only_field='value')  # type: ignore
            )
            _always_array = field_validator('my_data')(always_array(allow_empty=False))

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type=input_type,
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )
