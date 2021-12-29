"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Dict, List, Optional, Union

# third-party
import pytest
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_types import String, always_array, conditional_required, string
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

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            ('string', 'string', False, False),
            # required, empty input
            ('', '', False, False),
            # optional, empty input
            ('', '', True, False),
            # optional, null input
            (None, None, True, False),
            #
            # Fail Testing
            #
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

                my_data: String

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Optional[String]

        self._type_validation(
            PytestModel,
            input_name='my_data',
            input_value=input_value,
            input_type='String',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        (
            'input_value,expected,allow_empty,conditional_required_rules,'
            'max_length,min_length,regex,optional,fail_test'
        ),
        [
            #
            # Pass Testing
            #
            # required, normal input
            ('string', 'string', True, None, None, None, None, False, False),
            # required, empty input
            ('', '', True, None, None, None, None, False, False),
            # optional, empty input
            ('', '', True, None, None, None, None, True, False),
            # optional, null input
            (None, None, True, None, None, None, None, True, False),
            # required, normal input, max_length=10
            ('string', 'string', True, None, 10, None, None, False, False),
            # optional, normal input, max_length=10
            ('string', 'string', True, None, 10, None, None, True, False),
            # required, normal input, min_length=2
            ('string', 'string', True, None, None, 2, None, False, False),
            # optional, normal input, min_length=2
            ('string', 'string', True, None, None, 2, None, True, False),
            # required, normal input, regex=string
            ('string', 'string', True, None, None, None, r'^string$', True, False),
            # optional, null input, conditional_required=True
            (
                None,
                None,
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'optional'}],
                None,
                None,
                None,
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, True, None, None, None, None, False, True),
            # required, empty input, allow_empty=False
            ('', None, False, None, None, None, None, False, True),
            # required, empty input, conditional_required=True
            (
                '',
                'string',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                None,
                False,
                True,
            ),
            # required, null input, conditional_required=True
            (
                None,
                'string',
                True,
                [{'field': 'conditional', 'op': 'eq', 'value': 'required'}],
                None,
                None,
                None,
                False,
                True,
            ),
            # required, normal input, max_length=2
            ('string', 'string', True, None, 2, None, None, False, True),
            # optional, normal input, max_length=2
            ('string', 'string', True, None, 2, None, None, True, True),
            # required, normal input, min_length=10
            ('string', 'string', True, None, None, 10, None, False, True),
            # optional, normal input, min_length=10
            ('string', 'string', True, None, None, 10, None, True, True),
            # required, normal input, regex=string
            ('string', 'string', True, None, None, None, r'^string-extra$', True, True),
        ],
    )
    def test_field_model_string_custom_input(
        self,
        input_value: str,
        expected: str,
        allow_empty: bool,
        conditional_required_rules: Optional[List[Dict[str, str]]],
        max_length: int,
        min_length: int,
        regex: Optional[str],
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

                conditional: str = 'required'
                my_data: string(
                    allow_empty=allow_empty,
                    max_length=max_length,
                    min_length=min_length,
                    regex=regex,
                )

                _conditional_required = validator(
                    'my_data', allow_reuse=True, always=True, pre=True
                )(conditional_required(rules=conditional_required_rules))

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                conditional: str = 'required'
                my_data: Optional[
                    string(
                        allow_empty=allow_empty,
                        max_length=max_length,
                        min_length=min_length,
                        regex=regex,
                    )
                ]

                _conditional_required = validator(
                    'my_data', allow_reuse=True, always=True, pre=True
                )(conditional_required(rules=conditional_required_rules))

        self._type_validation(
            PytestModel,
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
            (['string'], ['string'], False, False),
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
    def test_field_model_string_array_input(
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

                my_data: List[String]

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Optional[List[String]]

        self._type_validation(
            PytestModel,
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
            ('string', ['string'], 'String', False, False),
            # required, array input
            (['string'], ['string'], 'StringArray', False, False),
            # required, empty string input
            ('', [''], 'String', False, False),
            # required, empty array input
            ([], [], 'StringArray', False, False),
            # optional, empty string input
            ('', [''], 'String', True, False),
            # optional, empty array input
            ([], [], 'StringArray', True, False),
            # optional, null input
            (None, [], 'String', True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, 'String', False, True),
        ],
    )
    def test_field_model_string_union_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
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

                my_data: Union[String, List[String]]

                _always_array = validator('my_data', allow_reuse=True)(always_array())

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Optional[Union[String, List[String]]]

                _always_array = validator('my_data', allow_reuse=True)(always_array())

        self._type_validation(
            PytestModel,
            input_name='my_data',
            input_value=input_value,
            input_type=input_type,
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )
