"""Testing TcEx Input module field types."""
# standard library
from collections.abc import Callable

# third-party
import pytest
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_type import (
    GroupEntity,
    IndicatorEntity,
    TCEntity,
    always_array,
    indicator_entity,
)
from tcex.input.model.app_playbook_model import AppPlaybookModel
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


# pylint: disable=no-self-argument
class TestInputsFieldTypes(InputTest):
    """Test TcEx String Field Model Tests."""

    def setup_method(self):
        """Configure setup before all tests."""
        # print('\n')  # print blank line for readability
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
            ),
            # required, string in -> int out
            (
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
            ),
            # optional, None
            (
                None,
                None,
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, null input
            (
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                False,
                True,
            ),
            # required, empty input
            (
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                False,
                True,
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            (
                {'id': '123', 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                True,
                True,
            ),
        ],
    )
    def test_field_model_tc_entity_input(
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

            my_data: TCEntity

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: TCEntity | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='TCEntity',
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
            # required, list input
            (
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                False,
                False,
            ),
            # required, string in -> int out
            (
                [{'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                False,
                False,
            ),
            # optional, None
            (
                None,
                None,
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, null input
            (
                [{'id': 123, 'type': 'Address', 'value': None, 'rating': '5'}],
                None,
                False,
                True,
            ),
            # required, empty input
            (
                [{'id': 123, 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                False,
                True,
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            (
                [{'id': '123', 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                True,
                True,
            ),
        ],
    )
    def test_field_model_tc_entity_array_input(
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

            my_data: list[TCEntity]

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: list[TCEntity] | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='TCEntityArray',
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
            # required, dict input
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntity',
                False,
                False,
            ),
            # required, list input
            (
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntityArray',
                False,
                False,
            ),
            # required, dict input, string value in -> int value out
            (
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntity',
                False,
                False,
            ),
            # required, list input, string value in -> int value out
            (
                [{'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntityArray',
                False,
                False,
            ),
            # optional, None TCEntity
            (
                None,
                [],
                'TCEntity',
                True,
                False,
            ),
            # optional, None TCEntityArray
            (
                None,
                [],
                'TCEntityArray',
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, tcentity, null input
            (
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                'TCEntity',
                False,
                True,
            ),
            # optional tcentity, null input
            (
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                'TCEntity',
                True,
                True,
            ),
            # required, tcentityarray, null input
            (
                [{'id': 123, 'type': 'Address', 'value': None, 'rating': '5'}],
                None,
                'TCEntityArray',
                False,
                True,
            ),
            # optional, tcentityarray, null input
            (
                [{'id': 123, 'type': 'Address', 'value': None, 'rating': '5'}],
                None,
                'TCEntityArray',
                True,
                True,
            ),
            # required, tcentity, empty input
            (
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                'TCEntity',
                False,
                True,
            ),
            # optional, tcentity, empty input
            (
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                'TCEntity',
                True,
                True,
            ),
            # required, tcentityarray, empty input
            (
                [{'id': 123, 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                'TCEntityArray',
                False,
                True,
            ),
            # optional, tcentityarray, empty input
            (
                [{'id': 123, 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                'TCEntityArray',
                True,
                True,
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     'TCEntityArray',
            #     False,
            #     True,
            # ),
            # required, None TCEntity
            (
                None,
                [],
                'TCEntity',
                False,
                True,
            ),
            # required, None TCEntityArray
            (
                None,
                [],
                'TCEntityArray',
                False,
                True,
            ),
        ],
    )
    def test_field_model_tc_entity_union_input(
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

            my_data: TCEntity | list[TCEntity]

            _always_array = validator('my_data', allow_reuse=True)(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: TCEntity | list[TCEntity] | None

            _always_array = validator('my_data', allow_reuse=True)(always_array())

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
        'input_value,expected,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
            ),
            # required, string in -> int out
            (
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
            ),
            # optional, None
            (
                None,
                None,
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, null input
            (
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                False,
                True,
            ),
            # required, empty input
            (
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                False,
                True,
            ),
            # required, wrong type
            (
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001', 'rating': '5'},
                None,
                False,
                True,
            ),
            # optional, wrong type
            (
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001', 'rating': '5'},
                None,
                True,
                True,
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            (
                {'id': '123', 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                True,
                True,
            ),
        ],
    )
    def test_field_model_indicator_entity_input(
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

            my_data: IndicatorEntity

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: IndicatorEntity | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='TCEntity',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        'input_value,expected,indicator_types,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, normal input
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                ['Address'],
                False,
                False,
            ),
            #
            # Fail Testing
            #
            (
                {'id': 123, 'type': 'Address', 'value': 'bad.com', 'rating': '5'},
                None,
                ['Host'],
                False,
                True,
            ),
        ],
    )
    def test_field_model_custom_indicator_entity_input(
        self,
        input_value: str,
        expected: str,
        indicator_types: list[str],
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ):
        """Test Binary field type.

        Playbook Data Type: String
        Validation: Not null
        """

        class PytestModelRequired(AppPlaybookModel):
            """Test Model for Inputs"""

            my_data: indicator_entity(indicator_types=indicator_types)  # type: ignore

        class PytestModelOptional(AppPlaybookModel):
            """Test Model for Inputs"""

            my_data: indicator_entity(indicator_types=indicator_types) | None  # type: ignore

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='TCEntity',
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
            (
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001'},
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001'},
                False,
                False,
            ),
            # required, string in -> int out
            (
                {'id': '123', 'type': 'Adversary', 'value': 'adversary-001'},
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001'},
                False,
                False,
            ),
            # optional, None
            (
                None,
                None,
                True,
                False,
            ),
            #
            # Fail Testing
            #
            # required, null input
            (
                {'id': 123, 'type': 'Adversary', 'value': None, 'rating': '5'},
                None,
                False,
                True,
            ),
            # required, empty input
            (
                {'id': 123, 'type': 'Adversary', 'value': '', 'rating': '5'},
                None,
                False,
                True,
            ),
            # required, wrong type
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                None,
                False,
                True,
            ),
            # optional, wrong type
            (
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                None,
                True,
                True,
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            (
                {'id': '123', 'type': 'Adversary', 'value': '', 'rating': '5'},
                None,
                True,
                True,
            ),
        ],
    )
    def test_field_model_group_entity_input(
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

            my_data: GroupEntity

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: GroupEntity | None

        pytest_model = PytestModelOptional
        if optional is False:
            pytest_model = PytestModelRequired

        self._type_validation(
            pytest_model,
            input_name='my_data',
            input_value=input_value,
            input_type='TCEntity',
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )
