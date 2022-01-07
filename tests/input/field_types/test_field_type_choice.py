"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.backports import cached_property
from tcex.input.field_types import Choice
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_types.utils import InputTest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx
    from tests.mock_app import MockApp


# pylint: disable=no-self-argument, no-self-use
class TestInputsFieldTypeChoice(InputTest):
    """Test TcEx Inputs Config."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    @staticmethod
    def test_field_type_choice(playbook_app: 'MockApp'):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': 'choice_1'}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice == 'choice_1'

    @staticmethod
    def test_field_type_choice_wrapped_with_optional(playbook_app: 'MockApp'):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Optional[Choice]

        config_data = {'my_choice': None}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice is None

    @staticmethod
    def test_field_type_choice_error_on_none(playbook_app: 'MockApp'):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': None}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_choice_assignment_test(playbook_app: 'MockApp'):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': 'choice_1'}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice == 'choice_1'

        tcex.inputs.model.my_choice = 'choice_2'
        assert tcex.inputs.model.my_choice == 'choice_2'

        tcex.inputs.model.my_choice = 'choice_3'
        assert tcex.inputs.model.my_choice == 'choice_3'

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
        playbook_app: 'MockApp',
    ):
        """Test Choice field type with string input.

        -- Select -- should be converted to None when accessing choice value

        Args:
            playbook_app (fixture): An instance of MockApp.
        """
        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_choice: Choice

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_choice_optional: Optional[Choice]

        self._type_validation(
            PytestModel,
            input_name='my_choice_optional' if optional else 'my_choice',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )
