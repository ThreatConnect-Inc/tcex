"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import Sensitive
from tcex.input.field_types.sensitive import sensitive
from tcex.pleb.scoped_property import scoped_property
from tests.input.field_types.utils import InputTest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx
    from tests.mock_app import MockApp


# pylint: disable=no-self-use
class TestInputsFieldTypeSensitive(InputTest):
    """Test TcEx Inputs Config."""

    def setup_method(self):
        """Configure setup before all tests."""
        # print('\n')  # print blank line for readability
        scoped_property._reset()

    @pytest.mark.parametrize(
        'input_value,expected,input_type,optional,fail_test',
        [
            #
            # Pass Testing
            #
            # required, str input
            ('secret', 'secret', 'String', False, False),
            # required, bytes input
            (b'secret', b'secret', 'Binary', False, False),
            # required, empty input
            ('', '', 'String', False, False),
            # optional, empty input
            ('', '', 'String', True, False),
            # optional, null input
            (None, None, 'String', True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, 'String', False, True),
        ],
    )
    def test_field_model_sensitive_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        optional: bool,
        fail_test: bool,
        playbook_app: 'MockApp',
    ):
        """Test field type."""

        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Sensitive

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Optional[Sensitive]

        self._type_validation(
            PytestModel,
            input_name='my_data',
            input_value=input_value,
            input_type=input_type,
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        ('input_value,expected,input_type,allow_empty,' 'max_length,min_length,optional,fail_test'),
        [
            #
            # Pass Testing
            #
            # required, bytes input
            ('secret', 'secret', 'String', True, None, None, False, False),
            # required, bytes input
            (b'secret', b'secret', 'Binary', True, None, None, False, False),
            # required, empty input
            ('', '', 'String', True, None, None, False, False),
            # optional, empty input
            ('', '', 'String', True, None, None, True, False),
            # optional, null input
            (None, None, 'String', True, None, None, True, False),
            # required, normal input, max_length=10
            ('secret', 'secret', 'String', True, 10, None, False, False),
            # optional, normal input, max_length=10
            ('secret', 'secret', 'String', True, 10, None, True, False),
            # required, normal input, min_length=2
            ('secret', 'secret', 'String', True, None, 2, False, False),
            # optional, normal input, min_length=2
            ('secret', 'secret', 'String', True, None, 2, True, False),
            #
            # Fail Testing
            #
            # required, null input
            (None, None, 'String', True, None, None, False, True),
            # required, empty input, allow_empty=False
            ('', None, 'String', False, None, None, False, True),
            # required, normal input, max_length=2
            ('secret', 'secret', 'String', True, 2, None, False, True),
            # optional, normal input, max_length=2
            ('secret', 'secret', 'String', True, 2, None, True, True),
            # required, normal input, min_length=10
            ('secret', 'secret', 'String', True, None, 10, False, True),
            # optional, normal input, min_length=10
            ('secret', 'secret', 'String', True, None, 10, True, True),
        ],
    )
    def test_field_model_sensitive_custom_input(
        self,
        input_value: str,
        expected: str,
        input_type: str,
        allow_empty: bool,
        max_length: int,
        min_length: int,
        optional: bool,
        fail_test: bool,
        playbook_app: 'MockApp',
    ):
        """Test field type."""
        if optional is False:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: sensitive(
                    allow_empty=allow_empty,
                    max_length=max_length,
                    min_length=min_length,
                )

        else:

            class PytestModel(BaseModel):
                """Test Model for Inputs"""

                my_data: Optional[
                    sensitive(
                        allow_empty=allow_empty,
                        max_length=max_length,
                        min_length=min_length,
                    )
                ]

        self._type_validation(
            PytestModel,
            input_name='my_data',
            input_value=input_value,
            input_type=input_type,
            expected=expected,
            fail_test=fail_test,
            playbook_app=playbook_app,
        )

    @pytest.mark.parametrize(
        'input_value,expected',
        [
            #
            # Pass Testing
            #
            # required, str input
            ('secret', 'secret'),
            # required, str input
            ('a-longer-example-of-a-secret', 'a-longer-example-of-a-secret'),
        ],
    )
    def test_field_type_sensitive_coverage(
        self, input_value: str, expected: str, playbook_app: 'MockApp'
    ):
        """Test field type."""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive: Sensitive

        config_data = {'my_sensitive': input_value}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert '****' in str(tcex.inputs.model.my_sensitive)
        assert tcex.inputs.model.my_sensitive.value == expected
        assert len(tcex.inputs.model.my_sensitive) == len(expected)
        assert isinstance(tcex.inputs.model.my_sensitive, Sensitive)

        # code coverage -> def:__modify_schema__
        tcex.inputs.model.schema()

        # code coverage -> def:validate->return value
        tcex.inputs.model.my_sensitive = tcex.inputs.model.my_sensitive

        # code coverage -> def:__repr__
        tcex.inputs.model.my_sensitive.__repr__()

        # code coverage -> Sensitive.__init__
        Sensitive(tcex.inputs.model.my_sensitive)

    @pytest.mark.parametrize(
        'input_value',
        [
            #
            # Fail Testing
            #
            # required, dict input
            ({}),
        ],
    )
    def test_field_type_sensitive_fail_coverage(self, input_value: str, playbook_app: 'MockApp'):
        """Test field type."""

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive: Sensitive

        config_data = {'my_sensitive': input_value}
        tcex: 'TcEx' = playbook_app(config_data=config_data).tcex

        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'validation error' in str(exc_info.value)
