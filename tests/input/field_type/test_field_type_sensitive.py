"""TestInputsFieldTypeSensitive for Sensitive field type validation.

This module contains comprehensive test cases for the Sensitive field type functionality
within the TcEx Framework, including validation of sensitive data handling, masking,
and various configuration options.

Classes:
    TestInputsFieldTypeSensitive: Test cases for Sensitive field type validation

TcEx Module Tested: tcex.input.field_type.sensitive
"""


from collections.abc import Callable


import pytest
from pydantic import BaseModel, ValidationError


from tcex.input.field_type import Sensitive
from tcex.input.field_type.sensitive import sensitive
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypeSensitive(InputTest):
    """TestInputsFieldTypeSensitive for Sensitive field type validation.

    This class provides comprehensive test coverage for Sensitive field types including
    validation of sensitive data handling, masking capabilities, custom configurations,
    and coverage testing for all Sensitive class methods.

    Fixtures:
        playbook_app: MockApp instance for testing field validation
    """

    def setup_method(self) -> None:
        """Configure setup before all tests."""
        # print('\n')  # print blank line for readability
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,input_type,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, str input
            pytest.param(
                'secret', 'secret', 'String', False, False, id='pass-required-string-input'
            ),
            # required, bytes input
            pytest.param(
                b'secret', b'secret', 'Binary', False, False, id='pass-required-bytes-input'
            ),
            # required, empty input
            pytest.param('', '', 'String', False, False, id='pass-required-empty-string'),
            # optional, empty input
            pytest.param('', '', 'String', True, False, id='pass-optional-empty-string'),
            # optional, null input
            pytest.param(None, None, 'String', True, False, id='pass-optional-null-input'),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(None, None, 'String', False, True, id='fail-required-null-input'),
        ],
    )
    def test_field_model_sensitive_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Sensitive field type with basic validation scenarios.

        This test validates the Sensitive field type with various input types including
        strings, bytes, empty values, and null values for both required and optional fields.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: Sensitive

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: Sensitive | None

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

    @pytest.mark.parametrize(
        ('input_value,expected,input_type,allow_empty,max_length,min_length,optional,fail_test'),
        [
            #
            # Pass Testing
            #
            # required, bytes input
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                None,
                None,
                False,
                False,
                id='pass-required-string-allow-empty',
            ),
            # required, bytes input
            pytest.param(
                b'secret',
                b'secret',
                'Binary',
                True,
                None,
                None,
                False,
                False,
                id='pass-required-binary-allow-empty',
            ),
            # required, empty input
            pytest.param(
                '',
                '',
                'String',
                True,
                None,
                None,
                False,
                False,
                id='pass-required-empty-allow-empty',
            ),
            # optional, empty input
            pytest.param(
                '',
                '',
                'String',
                True,
                None,
                None,
                True,
                False,
                id='pass-optional-empty-allow-empty',
            ),
            # optional, null input
            pytest.param(
                None,
                None,
                'String',
                True,
                None,
                None,
                True,
                False,
                id='pass-optional-null-allow-empty',
            ),
            # required, normal input, max_length=10
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                10,
                None,
                False,
                False,
                id='pass-required-max-length-valid',
            ),
            # optional, normal input, max_length=10
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                10,
                None,
                True,
                False,
                id='pass-optional-max-length-valid',
            ),
            # required, normal input, min_length=2
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                None,
                2,
                False,
                False,
                id='pass-required-min-length-valid',
            ),
            # optional, normal input, min_length=2
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                None,
                2,
                True,
                False,
                id='pass-optional-min-length-valid',
            ),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(
                None, None, 'String', True, None, None, False, True, id='fail-required-null-input'
            ),
            # required, empty input, allow_empty=False
            pytest.param(
                '',
                None,
                'String',
                False,
                None,
                None,
                False,
                True,
                id='fail-required-empty-disallow-empty',
            ),
            # required, normal input, max_length=2
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                2,
                None,
                False,
                True,
                id='fail-required-max-length-exceeded',
            ),
            # optional, normal input, max_length=2
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                2,
                None,
                True,
                True,
                id='fail-optional-max-length-exceeded',
            ),
            # required, normal input, min_length=10
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                None,
                10,
                False,
                True,
                id='fail-required-min-length-not-met',
            ),
            # optional, normal input, min_length=10
            pytest.param(
                'secret',
                'secret',
                'String',
                True,
                None,
                10,
                True,
                True,
                id='fail-optional-min-length-not-met',
            ),
        ],
    )
    def test_field_model_sensitive_custom_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        allow_empty: bool,
        max_length: int,
        min_length: int,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Sensitive field type with custom configuration options.

        This test validates the Sensitive field type with custom configuration options
        including allow_empty, max_length, and min_length constraints for both
        required and optional fields.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: sensitive(
                allow_empty=allow_empty,
                max_length=max_length,
                min_length=min_length,
            )  # type: ignore

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: None | (
                sensitive(
                    allow_empty=allow_empty,
                    max_length=max_length,
                    min_length=min_length,
                )
            )  # type: ignore

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

    @pytest.mark.parametrize(
        'input_value,expected',
        [
            #
            # Pass Testing
            #
            # required, str input
            pytest.param('secret', 'secret', id='pass-short-secret-string'),
            # required, str input
            pytest.param(
                'a-longer-example-of-a-secret',
                'a-longer-example-of-a-secret',
                id='pass-long-secret-string',
            ),
        ],
    )
    def test_field_type_sensitive_coverage(
        self, input_value: str, expected: str, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Sensitive field type comprehensive method coverage.

        This test provides comprehensive coverage of all Sensitive class methods including
        string representation, masking functionality, value access, length operations,
        and schema generation to ensure complete code coverage.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive: Sensitive

        config_data = {'my_sensitive': input_value}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert '****' in str(tcex.inputs.model.my_sensitive)  # type: ignore
        assert tcex.inputs.model.my_sensitive.value == expected  # type: ignore
        assert len(tcex.inputs.model.my_sensitive) == len(expected)  # type: ignore
        assert isinstance(tcex.inputs.model.my_sensitive, Sensitive)  # type: ignore

        # code coverage -> def:__modify_schema__
        tcex.inputs.model.schema()

        # TODO: [validate] this operation fails in pydantic v2
        # code coverage -> def:validate->return value
        # tcex.inputs.model.my_sensitive = tcex.inputs.model.my_sensitive  # type: ignore

        # code coverage -> def:__repr__
        tcex.inputs.model.my_sensitive.__repr__()  # type: ignore

        # code coverage -> Sensitive.__init__
        Sensitive(tcex.inputs.model.my_sensitive)  # type: ignore

    @pytest.mark.parametrize(
        'input_value',
        [
            #
            # Fail Testing
            #
            # required, dict input
            pytest.param({}, id='fail-invalid-dict-input'),
        ],
    )
    def test_field_type_sensitive_fail_coverage(
        self, input_value: str, playbook_app: Callable[..., MockApp]
    ) -> None:
        """Test Sensitive field type validation error handling.

        This test validates that the Sensitive field type properly raises ValidationError
        for invalid input types and provides appropriate error messages.

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive: Sensitive

        config_data = {'my_sensitive': input_value}
        tcex = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as ex:
            tcex.inputs.add_model(PytestModel)

        assert 'validation error' in str(ex.value)
