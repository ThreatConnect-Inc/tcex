"""Testing TcEx Input module field types."""
# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel

# first-party
from tcex.backports import cached_property
from tcex.input.field_types import EditChoice, edit_choice
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_types.utils import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


# pylint: disable=no-self-argument
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
            #
            # Fail Testing
            #
            # invalid choice
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
        playbook_app: Callable[..., MockApp],
    ):
        """Test EditChoice field type.

        Playbook Data Type: String
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_choice: EditChoice

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_choice: EditChoice | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_choice',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test,transformations,allow_additional',
        [
            #
            # Pass Testing
            #
            # required, normal input
            ('choice_1', 'choice_1', False, False, None, False),
            #
            # Test magic variable expansion
            #
            # pass in artifact type
            ('password', 'Password', False, False, None, False),
            # pass in attribute
            ('description', 'Description', False, False, None, False),
            # pass in group type
            ('Report', 'Report', False, False, None, False),
            # pass in indicator type
            ('Host', 'Host', False, False, None, False),
            # pass in Owner
            ('TCI', 'TCI', False, False, None, False),
            # optional, null input
            (None, None, True, False, None, False),
            # pass transformations dict, valid value should be transformed
            ('choice_1', 'Choice 1', False, False, {'choice_1': 'Choice 1'}, False),
            # pass transformations dict, value not transformed as it is not in transformations dict
            ('choice_1', 'choice_1', False, False, {'choice_2': 'Choice 2'}, False),
            #
            # Transformations when field is Optional
            # pass transformations dict, valid value should be transformed
            ('choice_1', 'Choice 1', True, False, {'choice_1': 'Choice 1'}, False),
            # pass transformations dict, value not transformed as it is not in transformations dict
            ('choice_1', 'choice_1', True, False, {'choice_2': 'Choice 2'}, False),
            #
            # invalid choice allowed because of allow_additional=True
            ('invalid_choice', 'invalid_choice', False, False, None, True),
            # same as above but with optional field
            ('invalid_choice', 'invalid_choice', True, False, None, True),
            #
            #
            # Fail Testing
            #
            # invalid choice
            ('invalid_choice', None, False, True, None, False),
            # required, empty input
            ('', '', False, True, None, False),
            # optional, empty input
            ('', '', True, True, None, False),
            # required, null input
            (None, None, False, True, None, False),
        ],
    )
    def test_custom_edit_choice_type(
        self,
        input_value: str,
        expected: str,
        optional: bool,
        fail_test: bool,
        allow_additional: bool,
        playbook_app: Callable[..., MockApp],
        transformations: dict,
    ):
        """Test Custom EditChoice field type.

        Playbook Data Type: String
        Validation: Not null
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_choice: edit_choice(
                value_transformations=transformations, allow_additional=allow_additional
            )  # type: ignore

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_choice: None | (
                edit_choice(
                    value_transformations=transformations, allow_additional=allow_additional
                )
            )  # type: ignore

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_choice',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )
