"""TestInputsFieldTypeChoice for Choice Field Type Testing.

This module provides comprehensive test cases for the Choice field type in TcEx Apps,
validating various input scenarios including basic functionality, optional fields,
assignment validation, select value handling, and custom choice transformations.

Classes:
    TestInputsFieldTypeChoice: Test suite for Choice field type validation

TcEx Module Tested: tcex.input.field_type.choice
"""

# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# first-party
from tcex.input.field_type import Choice, choice
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


class TestInputsFieldTypeChoice(InputTest):
    """TestInputsFieldTypeChoice for Choice Field Type Validation.

    This test class provides comprehensive validation of the Choice field type functionality
    in TcEx Apps, including testing basic choice selection, optional field handling,
    assignment validation, special value processing, and custom transformation features.

    Fixtures:
        playbook_app: MockApp fixture for creating test applications with choice field
            configurations
    """

    def setup_method(self) -> None:
        """Configure setup before all tests.

        This method resets cached and scoped properties to ensure clean test isolation.
        """
        scoped_property._reset()
        cached_property._reset()

    @staticmethod
    def test_field_type_choice(playbook_app: Callable[..., MockApp]) -> None:
        """Test Choice field type with string input.

        This test validates basic Choice field type functionality with a valid choice value.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': 'choice_1'}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice == 'choice_1'  # type: ignore

    @staticmethod
    def test_field_type_choice_wrapped_with_optional(playbook_app: Callable[..., MockApp]) -> None:
        """Test Choice field type with optional wrapper and None input.

        This test validates that optional Choice fields properly handle None values.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice | None

        config_data = {'my_choice': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice is None  # type: ignore

    @staticmethod
    def test_field_type_choice_error_on_none(playbook_app: Callable[..., MockApp]) -> None:
        """Test Choice field type validation error when None is provided to required field.

        This test validates that required Choice fields properly reject None values
        and raise appropriate validation errors.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as ex:
            tcex.inputs.add_model(PytestModel)

        assert 'Input should be a valid string' in str(ex.value)

    @staticmethod
    def test_field_type_choice_assignment_test(playbook_app: Callable[..., MockApp]) -> None:
        """Test Choice field type with validate_assignment enabled.

        This test validates that Choice fields properly validate assignments when
        validate_assignment=True is configured on the model, ensuring that both
        valid and invalid assignments are handled correctly.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            model_config = ConfigDict(validate_assignment=True)

            my_choice: Choice

        config_data = {'my_choice': 'choice_1'}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice == 'choice_1'  # type: ignore

        tcex.inputs.model.my_choice = 'choice_2'  # type: ignore
        assert tcex.inputs.model.my_choice == 'choice_2'  # type: ignore

        tcex.inputs.model.my_choice = 'choice_3'  # type: ignore
        assert tcex.inputs.model.my_choice == 'choice_3'  # type: ignore

        with pytest.raises(ValidationError) as ex:
            tcex.inputs.model.my_choice = None  # type: ignore

        assert 'Input should be a valid string' in str(ex.value)

        with pytest.raises(ValidationError) as ex:
            tcex.inputs.model.my_choice = 'Invalid Choice'  # type: ignore

        assert 'provided value Invalid Choice' in str(ex.value)

    @pytest.mark.parametrize(
        ('input_value,expected,optional,fail_test'),
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param('choice_1', 'choice_1', False, False, id='pass-required-normal-input'),
            # Choice input initialized with None (can happen in optional choice fields for job apps)
            pytest.param(None, None, True, False, id='pass-optional-none-input'),
            # Choice input initialized with -- Select -- special value
            pytest.param('-- Select --', None, True, False, id='pass-optional-select-value'),
            pytest.param('-- Select --', None, False, True, id='fail-required-select-value'),
        ],
    )
    def test_field_type_choice_select_value(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Choice field type with string input.

        This test case validates the Choice field type behavior with various input scenarios,
        including the special '-- Select --' value handling for both required and optional fields.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications

        Args:
            input_value: The input value to test
            expected: The expected output value after processing
            optional: Whether the field is optional or required
            fail_test: Whether the test should expect a failure
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice = Field(default=...)

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_choice_optional: Choice | None = Field(default=None)

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_choice_optional' if optional else 'my_choice',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        ('input_value,expected,optional,fail_test, transformations'),
        [
            #
            # Pass Testing
            #
            # required, normal input
            pytest.param(
                'choice_1', 'choice_1', False, False, None, id='pass-required-normal-input'
            ),
            # Input can be transformed
            pytest.param(
                'choice_1',
                'Choice 1',
                False,
                False,
                {'choice_1': 'Choice 1'},
                id='pass-required-transformed-input',
            ),
            # Input not transformed if not found in transformations
            pytest.param(
                'choice_1',
                'choice_1',
                False,
                False,
                {'choice_2': 'Choice 2'},
                id='pass-required-no-transformation',
            ),
            #
            # Transformations when field is optional
            # Input can be transformed
            pytest.param(
                'choice_1',
                'Choice 1',
                True,
                False,
                {'choice_1': 'Choice 1'},
                id='pass-optional-transformed-input',
            ),
            # Input not transformed if not found in transformations
            pytest.param(
                'choice_1',
                'choice_1',
                True,
                False,
                {'choice_2': 'Choice 2'},
                id='pass-optional-no-transformation',
            ),
            #
            # Choice input initialized with None (can happen in optional choice fields for job apps)
            pytest.param(None, None, True, False, None, id='pass-optional-none-input'),
            # Choice input initialized with -- Select -- special value
            pytest.param('-- Select --', None, True, False, None, id='pass-optional-select-value'),
            pytest.param('-- Select --', None, False, True, None, id='fail-required-select-value'),
            #
            # Fail Testing
            #
            # Invalid choice (should not be possible, adding for coverage)
            pytest.param('invalid_choice', None, False, True, None, id='fail-invalid-choice'),
            # Blank choice (should never happen, adding for coverage)
            pytest.param('', None, False, True, None, id='fail-empty-choice'),
        ],
    )
    def test_field_type_custom_choice(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        transformations: dict,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test Custom Choice field type with string input.

        This test case validates the custom Choice field type behavior with value transformations
        and various input scenarios including the special '-- Select --' value handling.

        Fixtures:
            playbook_app: MockApp fixture for creating test applications

        Args:
            input_value: The input value to test
            expected: The expected output value after processing
            optional: Whether the field is optional or required
            fail_test: Whether the test should expect a failure
            transformations: Dictionary for value transformations
            playbook_app: MockApp fixture for creating test applications
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_choice: choice(value_transformations=transformations)  # type: ignore

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_choice_optional: choice(value_transformations=transformations) | None  # type: ignore

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_choice_optional' if optional else 'my_choice',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )
