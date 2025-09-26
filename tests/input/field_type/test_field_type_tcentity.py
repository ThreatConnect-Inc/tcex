"""TestInputsFieldTypes for TCEntity field type validation.

This module contains comprehensive test cases for the TCEntity field type functionality
within the TcEx Framework, including validation of single entities, arrays, union types,
and specialized entity types like IndicatorEntity and GroupEntity.

Classes:
    TestInputsFieldTypes: Test cases for TCEntity field type validation

TcEx Module Tested: tcex.input.field_type.tcentity
"""


from collections.abc import Callable


import pytest
from pydantic import BaseModel, field_validator


from tcex.input.field_type import (GroupEntity, IndicatorEntity, TCEntity,
                                   always_array, indicator_entity)
from tcex.input.model.app_playbook_model import AppPlaybookModel
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING


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
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
                id='pass-required-normal-entity',
            ),
            # required, string in -> int out
            pytest.param(
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
                id='pass-required-string-to-int-conversion',
            ),
            # optional, None
            pytest.param(
                None,
                None,
                True,
                False,
                id='pass-optional-null-input',
            ),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-null-value',
            ),
            # required, empty input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-empty-value',
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            pytest.param(
                {'id': '123', 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                True,
                True,
                id='fail-optional-empty-value',
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
    ) -> None:
        """Test TCEntity field type with single entity validation.

        Validates TCEntity field type with various input scenarios including single entity
        dict input, string to integer type coercion for id/rating fields, required vs
        optional field validation, and null/empty value handling with proper error cases.

        Playbook Data Type: TCEntity
        Validation: Entity structure validation, type coercion, required field presence

        Args:
            input_value: Input value to validate (dict, None, etc.)
            expected: Expected output after validation
            optional: Whether field is optional
            fail_test: Whether test should fail validation
            playbook_app: Mock app fixture for testing

        Fixtures:
            playbook_app: MockApp instance for testing field validation
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
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                False,
                False,
                id='pass-required-entity-array',
            ),
            # required, string in -> int out
            pytest.param(
                [{'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                False,
                False,
                id='pass-required-array-string-to-int-conversion',
            ),
            # optional, None
            pytest.param(
                None,
                None,
                True,
                False,
                id='pass-optional-null-input',
            ),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': None, 'rating': '5'}],
                None,
                False,
                True,
                id='fail-required-array-null-value',
            ),
            # required, empty input
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                False,
                True,
                id='fail-required-array-empty-value',
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            pytest.param(
                [{'id': '123', 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                True,
                True,
                id='fail-optional-array-empty-value',
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
    ) -> None:
        """Test TCEntity field type with array validation.

        Validates TCEntity field type in array format with various scenarios including
        valid entity arrays, string to integer type coercion, null/empty values, and
        validation errors for both required and optional array fields.

        Playbook Data Type: list[TCEntity]
        Validation: Array structure validation, entity validation, type coercion

        Args:
            input_value: Input value to validate (list, None, etc.)
            expected: Expected output after validation
            optional: Whether field is optional
            fail_test: Whether test should fail validation
            playbook_app: Mock app fixture for testing

        Fixtures:
            playbook_app: MockApp instance for testing field validation
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
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntity',
                False,
                False,
                id='pass-required-single-entity-to-array',
            ),
            # required, list input
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntityArray',
                False,
                False,
                id='pass-required-entity-array',
            ),
            # required, dict input, string value in -> int value out
            pytest.param(
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntity',
                False,
                False,
                id='pass-required-single-entity-string-to-int',
            ),
            # required, list input, string value in -> int value out
            pytest.param(
                [{'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'}],
                [{'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5}],
                'TCEntityArray',
                False,
                False,
                id='pass-required-array-entity-string-to-int',
            ),
            # optional, None TCEntity
            pytest.param(
                None,
                [],
                'TCEntity',
                True,
                False,
                id='pass-optional-null-entity-to-array',
            ),
            # optional, None TCEntityArray
            pytest.param(
                None,
                [],
                'TCEntityArray',
                True,
                False,
                id='pass-optional-null-array-to-array',
            ),
            #
            # Fail Testing
            #
            # required, tcentity, null input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                'TCEntity',
                False,
                True,
                id='fail-required-entity-null-value',
            ),
            # optional tcentity, null input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                'TCEntity',
                True,
                True,
                id='fail-optional-entity-null-value',
            ),
            # required, tcentityarray, null input
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': None, 'rating': '5'}],
                None,
                'TCEntityArray',
                False,
                True,
                id='fail-required-array-null-value',
            ),
            # optional, tcentityarray, null input
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': None, 'rating': '5'}],
                None,
                'TCEntityArray',
                True,
                True,
                id='fail-optional-array-null-value',
            ),
            # required, tcentity, empty input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                'TCEntity',
                False,
                True,
                id='fail-required-entity-empty-value',
            ),
            # optional, tcentity, empty input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                'TCEntity',
                True,
                True,
                id='fail-optional-entity-empty-value',
            ),
            # required, tcentityarray, empty input
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                'TCEntityArray',
                False,
                True,
                id='fail-required-array-empty-value',
            ),
            # optional, tcentityarray, empty input
            pytest.param(
                [{'id': 123, 'type': 'Address', 'value': '', 'rating': '5'}],
                None,
                'TCEntityArray',
                True,
                True,
                id='fail-optional-array-empty-value',
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
            pytest.param(
                None,
                [],
                'TCEntity',
                False,
                True,
                id='fail-required-null-entity',
            ),
            # required, None TCEntityArray
            pytest.param(
                None,
                [],
                'TCEntityArray',
                False,
                True,
                id='fail-required-null-array',
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
    ) -> None:
        """Test TCEntity field type with union validation and always_array.

        Validates TCEntity field type as a union of single entity or array with always_array
        validator applied. Tests single entity to array conversion, array handling, null/empty
        values, and validation errors for both required and optional union fields.

        Playbook Data Type: TCEntity | list[TCEntity] (with always_array validator)
        Validation: Union type handling, array conversion, entity validation

        Args:
            input_value: Input value to validate (dict, list, None, etc.)
            expected: Expected output after validation
            input_type: Type specification for the test case
            optional: Whether field is optional
            fail_test: Whether test should fail validation
            playbook_app: Mock app fixture for testing

        Fixtures:
            playbook_app: MockApp instance for testing field validation
        """

        class PytestModelRequired(BaseModel):
            """Test Model for Inputs"""

            my_data: TCEntity | list[TCEntity]

            _always_array = field_validator('my_data')(always_array())

        class PytestModelOptional(BaseModel):
            """Test Model for Inputs"""

            my_data: TCEntity | list[TCEntity] | None

            _always_array = field_validator('my_data')(always_array())

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
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
                id='pass-required-normal-input',
            ),
            # required, string in -> int out
            pytest.param(
                {'id': '123', 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                False,
                False,
                id='pass-required-string-to-int',
            ),
            # optional, None
            pytest.param(
                None,
                None,
                True,
                False,
                id='pass-optional-none-input',
            ),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': None, 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-null-value',
            ),
            # required, empty input
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-empty-value',
            ),
            # required, wrong type
            pytest.param(
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001', 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-wrong-type',
            ),
            # optional, wrong type
            pytest.param(
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001', 'rating': '5'},
                None,
                True,
                True,
                id='fail-optional-wrong-type',
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            pytest.param(
                {'id': '123', 'type': 'Address', 'value': '', 'rating': '5'},
                None,
                True,
                True,
                id='fail-optional-invalid-data',
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
    ) -> None:
        """Test IndicatorEntity field type validation.

        Validates IndicatorEntity field type with various scenarios including normal indicator
        entities, string to integer type coercion, null/empty values, wrong entity types, and
        validation errors for both required and optional indicator entity fields.

        Playbook Data Type: IndicatorEntity
        Validation: Indicator-specific entity validation, type checking, field presence

        Args:
            input_value: Input value to validate (dict, None, etc.)
            expected: Expected output after validation
            optional: Whether field is optional
            fail_test: Whether test should fail validation
            playbook_app: Mock app fixture for testing

        Fixtures:
            playbook_app: MockApp instance for testing field validation
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
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': 5},
                ['Address'],
                False,
                False,
                id='pass-required-normal-input',
            ),
            #
            # Fail Testing
            #
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': 'bad.com', 'rating': '5'},
                None,
                ['Host'],
                False,
                True,
                id='fail-wrong-indicator-type',
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
    ) -> None:
        """Test custom indicator entity field type with type restrictions.

        Validates custom indicator entity field type with specific indicator type restrictions.
        Tests scenarios with correct indicator types, wrong indicator types for validation
        failures, and ensures proper type checking against allowed indicator types.

        Playbook Data Type: indicator_entity with type restrictions
        Validation: Indicator type matching, custom type validation

        Args:
            input_value: Input value to validate (dict, None, etc.)
            expected: Expected output after validation
            indicator_types: List of allowed indicator types
            optional: Whether field is optional
            fail_test: Whether test should fail validation
            playbook_app: Mock app fixture for testing

        Fixtures:
            playbook_app: MockApp instance for testing field validation
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
            pytest.param(
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001'},
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001'},
                False,
                False,
                id='pass-required-normal-input',
            ),
            # required, string in -> int out
            pytest.param(
                {'id': '123', 'type': 'Adversary', 'value': 'adversary-001'},
                {'id': 123, 'type': 'Adversary', 'value': 'adversary-001'},
                False,
                False,
                id='pass-required-string-to-int',
            ),
            # optional, None
            pytest.param(
                None,
                None,
                True,
                False,
                id='pass-optional-none-input',
            ),
            #
            # Fail Testing
            #
            # required, null input
            pytest.param(
                {'id': 123, 'type': 'Adversary', 'value': None, 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-null-value',
            ),
            # required, empty input
            pytest.param(
                {'id': 123, 'type': 'Adversary', 'value': '', 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-empty-value',
            ),
            # required, wrong type
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                None,
                False,
                True,
                id='fail-required-wrong-type',
            ),
            # optional, wrong type
            pytest.param(
                {'id': 123, 'type': 'Address', 'value': '1.1.1.1', 'rating': '5'},
                None,
                True,
                True,
                id='fail-optional-wrong-type',
            ),
            # required, missing field
            # (
            #     {'id': 123, 'value': '1.1.1.1', 'rating': '5'},
            #     None,
            #     False,
            #     True,
            # ),
            # optional, Invalid data
            pytest.param(
                {'id': '123', 'type': 'Adversary', 'value': '', 'rating': '5'},
                None,
                True,
                True,
                id='fail-optional-invalid-data',
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
    ) -> None:
        """Test GroupEntity field type validation.

        Validates GroupEntity field type with various scenarios including normal group entities,
        string to integer type coercion, null/empty values, wrong entity types (like Address
        instead of Adversary), and validation errors for both required and optional group fields.

        Playbook Data Type: GroupEntity
        Validation: Group-specific entity validation, type checking, field presence

        Args:
            input_value: Input value to validate (dict, None, etc.)
            expected: Expected output after validation
            optional: Whether field is optional
            fail_test: Whether test should fail validation
            playbook_app: Mock app fixture for testing

        Fixtures:
            playbook_app: MockApp instance for testing field validation
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
