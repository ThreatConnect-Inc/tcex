"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import Choice

from .utils import InputTest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx
    from tests.mock_app import MockApp


class TestInputsFieldTypeChoice(InputTest):
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_field_type_choice(playbook_app: 'MockApp'):
        """Test Choice field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': 'Valid Choice'}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice.value == 'Valid Choice'

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

        config_data = {'my_choice': 'Initial Value'}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice.value == 'Initial Value'

        tcex.inputs.model.my_choice = Choice('Second Choice')
        assert isinstance(tcex.inputs.model.my_choice, Choice)
        assert tcex.inputs.model.my_choice.value == 'Second Choice'

        tcex.inputs.model.my_choice = 'Another Choice'
        assert isinstance(tcex.inputs.model.my_choice, Choice)
        assert tcex.inputs.model.my_choice.value == 'Another Choice'

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.model.my_choice = None

        assert 'none is not an allowed value' in str(exc_info.value)

    @staticmethod
    def test_field_type_choice_select_value(playbook_app: 'MockApp'):
        """Test Choice field type with string input.

        -- Select -- should be converted to None when accessing choice value

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_choice: Choice

        config_data = {'my_choice': '-- Select --'}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        assert tcex.inputs.model.my_choice.value is None
