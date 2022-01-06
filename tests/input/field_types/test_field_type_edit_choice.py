"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel

# first-party
from tcex.backports import cached_property
from tcex.input.field_types import EditChoice
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_types.utils import InputTest

if TYPE_CHECKING:
    # first-party
    from tests.mock_app import MockApp


# pylint: disable=no-self-argument, no-self-use
class TestInputsFieldTypes(InputTest):
    """Test TcEx String Field Model Tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            ('choice_1', 'choice_1', False, False),
            # optional, null input
            (None, None, True, False),
            # #
            # Fail Testing
            #
            # required, invalid input
            ('invalid_choice', None, False, True),
            # required, empty input
            ('', '', False, True),
            # optional, empty input
            ('', '', True, True),
            # required, null input
            (None, None, False, True),
        ],
    )
    def test_field_model_string_input(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        playbook_app: 'MockApp',
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
        """

        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_choice: EditChoice

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_choice: Optional[EditChoice]

        self._type_validation(
            PytestModel,
            input_name='my_choice',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )
