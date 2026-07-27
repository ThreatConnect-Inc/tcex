"""TestInputsFieldTypes for testing EditChoice field type functionality.

This module contains comprehensive test cases for the EditChoice field type implementation in TcEx,
including validation of choice inputs, transformations, and optional/required field behaviors.

Classes:
    TestInputsFieldTypes: Test class for EditChoice field type validation

TcEx Module Tested: tcex.input.field_type.EditChoice
"""

from collections.abc import Callable
from typing import Annotated, Any

import pytest
from pydantic import BaseModel, ValidationError
from tests.input.field_type.util import InputTest
from tests.mock_app import MockApp  # TYPE-CHECKING

from tcex.input.field_type import EditChoice, edit_choice
from tcex.pleb.cached_property import cached_property
from tcex.pleb.scoped_property import scoped_property


class TestInputsFieldTypes(InputTest):
    """TestInputsFieldTypes for comprehensive EditChoice field type testing.

    This class provides extensive test coverage for the EditChoice field type, including validation
    of choice selections, transformations, optional/required behaviors, and error conditions.

    Fixtures:
        playbook_app: Mock application fixture for testing TcEx functionality
    """

    def setup_method(self) -> None:
        """Configure setup before all tests."""
        scoped_property._reset()
        cached_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,optional,fail_test',
        [
            pytest.param('choice_1', 'choice_1', False, False, id='pass-required-valid-choice'),
            pytest.param(None, None, True, False, id='pass-optional-none-input'),
            pytest.param('invalid_choice', None, False, True, id='fail-invalid-choice'),
            pytest.param('', '', False, True, id='fail-required-empty-input'),
            pytest.param('', '', True, True, id='fail-optional-empty-input'),
            pytest.param(None, None, False, True, id='fail-required-none-input'),
        ],
    )
    def test_field_model_string_input(
        self,
        input_value: Any,
        expected: Any,
        optional: bool,
        fail_test: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test EditChoice field type with basic choice validation.

        Tests the basic EditChoice field type functionality including valid/invalid choices,
        required vs optional field behaviors, and empty input handling.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
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
            pytest.param(
                'bsummers@threatconnect.com',
                'bsummers@threatconnect.com',
                False,
                False,
                None,
                False,
                id='pass-normal-input',
            ),
            pytest.param(
                '${users:bsummers@threatconnect.com}',
                'bsummers@threatconnect.com',
                False,
                False,
                None,
                False,
                id='pass-normal-users-variable',
            ),
            pytest.param(
                '${user_groups:bsummers@threatconnect.com}',
                'bsummers@threatconnect.com',
                False,
                False,
                None,
                False,
                id='pass-normal-user_groups-variable',
            ),
            pytest.param(
                'choice_1', 'choice_1', False, False, None, False, id='pass-required-valid-choice'
            ),
            pytest.param(
                'password', 'Password', False, False, None, False, id='pass-artifact-type-password'
            ),
            pytest.param(
                'description',
                'Description',
                False,
                False,
                None,
                False,
                id='pass-attribute-description',
            ),
            pytest.param(
                'Report', 'Report', False, False, None, False, id='pass-group-type-report'
            ),
            pytest.param('Host', 'Host', False, False, None, False, id='pass-indicator-type-host'),
            pytest.param('TCI', 'TCI', False, False, None, False, id='pass-owner-tci'),
            pytest.param(None, None, True, False, None, False, id='pass-optional-none-input'),
            pytest.param(
                'choice_1',
                'Choice 1',
                False,
                False,
                {'choice_1': 'Choice 1'},
                False,
                id='pass-transformations-matched',
            ),
            pytest.param(
                'choice_1',
                'choice_1',
                False,
                False,
                {'choice_2': 'Choice 2'},
                False,
                id='pass-transformations-unmatched',
            ),
            pytest.param(
                'choice_1',
                'Choice 1',
                True,
                False,
                {'choice_1': 'Choice 1'},
                False,
                id='pass-optional-transformations-matched',
            ),
            pytest.param(
                'choice_1',
                'choice_1',
                True,
                False,
                {'choice_2': 'Choice 2'},
                False,
                id='pass-optional-transformations-unmatched',
            ),
            pytest.param(
                'invalid_choice',
                'invalid_choice',
                False,
                False,
                None,
                True,
                id='pass-invalid-choice-allowed',
            ),
            pytest.param(
                'invalid_choice',
                'invalid_choice',
                True,
                False,
                None,
                True,
                id='pass-optional-invalid-choice-allowed',
            ),
            pytest.param(
                'invalid_choice',
                None,
                False,
                True,
                None,
                False,
                id='fail-invalid-choice-not-allowed',
            ),
            pytest.param('', '', False, True, None, False, id='fail-required-empty-input'),
            pytest.param('', '', True, True, None, False, id='fail-optional-empty-input'),
            pytest.param(None, None, False, True, None, False, id='fail-required-none-input'),
        ],
    )
    def test_custom_edit_choice_type(
        self,
        input_value: Any,
        expected: Any,
        optional: bool,
        fail_test: bool,
        allow_additional: bool,
        playbook_app: Callable[..., MockApp],
        transformations: dict[str, str] | None,
    ) -> None:
        """Test custom EditChoice field type with advanced features.

        Tests the custom EditChoice field type functionality including value transformations,
        magic variable expansion (artifact types, attributes, group types, indicator types),
        allow_additional option, and validation of various input combinations.

        Fixtures:
            playbook_app: Mock application fixture for testing TcEx functionality
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


class TestEditChoiceAnnotated:
    """Test EditChoice field type via Annotated[str, edit_choice(...)] syntax.

    Exercises the annotated-metadata chaining contract so that
    edit_choice(...) factory constraints take effect when the type is written
    as Annotated[str, edit_choice(...)] rather than as a bare EditChoice subclass.

    EditChoice validation reads install.json via InstallJson() and accesses
    registry.session_tc for variable resolution, so the playbook_app fixture
    is required to initialize the registry before any model is validated.
    Using allow_additional=True avoids needing specific valid_values in
    install.json — any non-empty string passes through.
    """

    def setup_method(self) -> None:
        """Configure setup before each test."""
        scoped_property._reset()  # noqa: SLF001
        cached_property._reset()  # noqa: SLF001

    @pytest.mark.parametrize(
        argnames='input_value,should_fail',
        argvalues=[
            pytest.param(
                # any non-empty string passes when allow_additional=True
                'any_value',
                False,
                id='pass-any-non-empty-string',
            ),
            pytest.param(
                # another arbitrary string also passes
                'another_value',
                False,
                id='pass-another-non-empty-string',
            ),
            pytest.param(
                # empty string is always rejected at the EditChoice level
                '',
                True,
                id='fail-empty-string-rejected',
            ),
        ],
    )
    def test_edit_choice_annotated(
        self,
        input_value: str,
        should_fail: bool,
        playbook_app: Callable[..., MockApp],
    ) -> None:
        """Test EditChoice via Annotated with allow_additional=True.

        The playbook_app fixture initializes the registry (registry.session_tc)
        that EditChoice validation needs to resolve TC variables in valid_values.
        The model is still instantiated directly via BaseModel, not through the
        TcEx input pipeline.
        """
        # Initialize registry + install.json by touching .tcex; no TC server needed
        # because valid_values resolves to [] (field 'x' absent from mock install.json).
        _ = playbook_app().tcex

        class M(BaseModel):
            x: Annotated[str, edit_choice(allow_additional=True)]

        if should_fail:
            with pytest.raises(ValidationError):
                M(x=input_value)
        else:
            result = M(x=input_value)
            assert result.x == input_value, f'Expected {input_value!r}, got {result.x!r}'
