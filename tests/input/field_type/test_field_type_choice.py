"""Testing TcEx Input module field types."""
# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex import TcEx  # TYPE-CHECKING
from tcex.backport import cached_property
from tcex.input.field_type import Choice, choice
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


# pylint: disable=no-self-argument
class TestInputsFieldTypeChoice(InputTest):
    """Test TcEx Inputs Config."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    @staticmethod
    def test_field_type_choice(playbook_app: Callable[..., MockApp]):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': 'choice_1'}
        tcex: TcEx = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice == 'choice_1'  # type: ignore

    @staticmethod
    def test_field_type_choice_wrapped_with_optional(playbook_app: Callable[..., MockApp]):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice | None

        config_data = {'my_choice': None}
        tcex: TcEx = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice is None  # type: ignore

    @staticmethod
    def test_field_type_choice_error_on_none(playbook_app: Callable[..., MockApp]):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': None}
        tcex: TcEx = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_choice_assignment_test(playbook_app: Callable[..., MockApp]):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': 'choice_1'}
        tcex: TcEx = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice == 'choice_1'  # type: ignore

        tcex.inputs.model.my_choice = 'choice_2'
        assert tcex.inputs.model.my_choice == 'choice_2'  # type: ignore

        tcex.inputs.model.my_choice = 'choice_3'
        assert tcex.inputs.model.my_choice == 'choice_3'  # type: ignore

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.model.my_choice = None

        assert 'none' in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.model.my_choice = 'Invalid Choice'

        print(exc_info.value)
        assert 'valid value' in str(exc_info.value)

    @pytest.mark.parametrize(
        ('input_value,expected,optional,fail_test'),
        [
            #
            # Pass Testing
            #
            # required, normal input
            ('choice_1', 'choice_1', False, False),
            # Choice input initialized with None (can happen in optional choice fields for job apps)
            (None, None, True, False),
            # Choice input initialized with -- Select -- special value
            ('-- Select --', None, True, False),
            ('-- Select --', None, False, True),
        ],
    )
    def test_field_type_choice_select_value(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Choice field type with string input.

        -- Select -- should be converted to None when accessing choice value

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_choice_optional: Choice | None

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
            ('choice_1', 'choice_1', False, False, None),
            # Input can be transformed
            ('choice_1', 'Choice 1', False, False, {'choice_1': 'Choice 1'}),
            # Input not transformed if not found in transformations
            ('choice_1', 'choice_1', False, False, {'choice_2': 'Choice 2'}),
            #
            # Transformations when field is optional
            # Input can be transformed
            ('choice_1', 'Choice 1', True, False, {'choice_1': 'Choice 1'}),
            # Input not transformed if not found in transformations
            ('choice_1', 'choice_1', True, False, {'choice_2': 'Choice 2'}),
            #
            # Choice input initialized with None (can happen in optional choice fields for job apps)
            (None, None, True, False, None),
            # Choice input initialized with -- Select -- special value
            ('-- Select --', None, True, False, None),
            ('-- Select --', None, False, True, None),
            #
            # Fail Testing
            #
            # Invalid choice (should not be possible, adding for coverage)
            ('invalid_choice', None, False, True, None),
            # Blank choice (should never happen, adding for coverage)
            ('', None, False, True, None),
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
    ):
        """Test Custom Choice field type with string input.

        -- Select -- should be converted to None when accessing choice value

        Args:
            playbook_app (fixture): An instance of MockApp.
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
