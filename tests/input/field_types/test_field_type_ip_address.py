"""Testing TcEx Input module field types."""
# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_types import AddressEntity, IpAddress, always_array, entity_input, ip_address
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_types.utils import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


# pylint: disable=no-self-argument
class TestInputsIpAddressFieldTypes(InputTest):
    """Test TcEx String Field Model Tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            ('1.1.1.1', '1.1.1.1', False, False),
            # optional, null input
            (None, None, True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, False, True),
            # required, invalid IP
            ('not-an-ip', None, False, True),
        ],
    )
    def test_field_model_ip_address_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
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
            ('1.1.1.1', '1.1.1.1', False, False, False),
            # required, ip with port input
            ('1.1.1.1:443', '1.1.1.1', True, False, False),
            # optional, null input
            (None, None, False, True, False),
            #
            # Fail Testing
            #
            # required, ip with port input
            ('1.1.1.1:443', None, False, False, True),
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
    ):
        """Test IP Address field type."""

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
            (['1.1.1.1'], ['1.1.1.1'], False, False),
            # required, empty input
            ([], [], False, False),
            # optional, empty input
            ([], [], True, False),
            # optional, null input
            (None, None, True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, False, True),
        ],
    )
    def test_field_model_ip_address_array_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
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
            ('1.1.1.1', ['1.1.1.1'], 'String', False, False),
            # required, string input
            (
                '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
                ['2001:0db8:85a3:0000:0000:8a2e:0370:7334'],
                'String',
                False,
                False,
            ),
            # required, array input
            (['1.1.1.1'], ['1.1.1.1'], 'StringArray', False, False),
            # required, tcentity
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1'},
                ['1.1.1.1'],
                'TCEntity',
                False,
                False,
            ),
            # required, tcentity array
            (
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1'}],
                ['1.1.1.1'],
                'TCEntityArray',
                False,
                False,
            ),
            #
            # Fail Testing
            #
            # required, tcentity
            (
                {'id': 123, 'type': 'Host', 'value': 'bad.com'},
                None,
                'TCEntity',
                False,
                True,
            ),
            # required, null input
            (None, None, 'String', False, True),
            # required, empty array input
            ([], [], 'StringArray', False, True),
            # optional, empty array input
            ([], [], 'StringArray', True, True),
            # optional, empty string input
            ('', [], 'String', True, True),
            # optional, null input
            (None, [], 'String', True, True),
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
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: (
                list[IpAddress] | IpAddress | list[AddressEntity] | AddressEntity  # type: ignore
            )

            _entity_input = validator('my_data', allow_reuse=True)(
                entity_input(only_field='value')  # type: ignore
            )
            _always_array = validator('my_data', allow_reuse=True)(always_array(allow_empty=False))

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: (
                None
                | (
                    list[IpAddress]
                    | IpAddress
                    | list[AddressEntity]  # type: ignore
                    | AddressEntity  # type: ignore
                )
            )

            _entity_input = validator('my_data', allow_reuse=True)(
                entity_input(only_field='value')  # type: ignore
            )
            _always_array = validator('my_data', allow_reuse=True)(always_array(allow_empty=False))

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
