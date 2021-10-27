"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING, Optional

# third-party
import pytest
from pydantic import BaseModel, ValidationError

# first-party
from tcex.input.field_types import Sensitive, SensitiveOptional
from .utils import InputTest


if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeSensitive(InputTest):
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_field_type_sensitive(playbook_app: 'MockApp'):
        """Test Sensitive field type with string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive: Sensitive

        config_data = {'my_sensitive': 'super-secret-squirrel'}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)
        # print(tcex.inputs.data.json(indent=2))

        assert str(tcex.inputs.data.my_sensitive).startswith('****')
        assert tcex.inputs.data.my_sensitive.value == config_data.get('my_sensitive')
        assert len(tcex.inputs.data.my_sensitive) == len(config_data.get('my_sensitive'))
        assert isinstance(tcex.inputs.data.my_sensitive, Sensitive)

        # code coverage -> def:__modify_schema__
        tcex.inputs.data.schema()

        # code coverage -> def:validate->return value
        tcex.inputs.data.my_sensitive = tcex.inputs.data.my_sensitive

        # code coverage -> def:__repr__
        tcex.inputs.data.my_sensitive.__repr__()

    def test_field_type_sensitive_input_binary_string_staged(self, playbook_app: 'MockApp'):
        """Test Sensitive field type with binary input.

        Input value staged in key value store.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: Sensitive

        config_data = {'my_sensitive_field': '#App:1234:my_sensitive_field!Binary'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(
            'my_sensitive_field', '#App:1234:my_sensitive_field!Binary', b'binary string', tcex
        )
        tcex.inputs.add_model(PytestModel)

        assert str(tcex.inputs.data.my_sensitive_field).startswith('****')
        assert tcex.inputs.data.my_sensitive_field.value == b'binary string'

    @staticmethod
    def test_field_type_sensitive_input_null_not_allowed(playbook_app: 'MockApp'):
        """Test Sensitive field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: Sensitive

        config_data = {'my_sensitive_field': None}
        tcex = playbook_app(config_data=config_data).tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'none is not an allowed value' in str(exc_info.value)

    def test_field_type_sensitive_input_blank_binary_not_allowed(self, playbook_app: 'MockApp'):
        """Test Sensitive field type with blank binary input.

        Error expected as this field is Sensitive and not SensitiveOptional

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: Sensitive

        config_data = {'my_sensitive_field': '#App:1234:my_sensitive_field!Binary'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(
            'my_sensitive_field', '#App:1234:my_sensitive_field!Binary', b'', tcex
        )
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Sensitive value may not be empty' in str(exc_info.value)

    def test_field_type_sensitive_input_blank_string_not_allowed(self, playbook_app: 'MockApp'):
        """Test Sensitive field type with blank string input.

        Error expected as this field is Sensitive and not SensitiveOptional

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: Sensitive

        config_data = {'my_sensitive_field': '#App:1234:my_sensitive_field!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(
            'my_sensitive_field', '#App:1234:my_sensitive_field!String', '', tcex
        )
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Sensitive value may not be empty' in str(exc_info.value)

    def test_field_type_sensitive_input_blank_binary_allowed(self, playbook_app: 'MockApp'):
        """Test SensitiveOptional field type with blank binary input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: SensitiveOptional

        config_data = {'my_sensitive_field': '#App:1234:my_sensitive_field!Binary'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(
            'my_sensitive_field', '#App:1234:my_sensitive_field!Binary', b'', tcex
        )
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_sensitive_field.value == b''

    def test_field_type_sensitive_input_blank_string_allowed(self, playbook_app: 'MockApp'):
        """Test SensitiveOptional field type with blank string input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: SensitiveOptional

        config_data = {'my_sensitive_field': '#App:1234:my_sensitive_field!String'}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        self._stage_key_value(
            'my_sensitive_field', '#App:1234:my_sensitive_field!String', '', tcex
        )
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_sensitive_field.value == ''

    @staticmethod
    def test_field_type_sensitive_input_null_allowed(playbook_app: 'MockApp'):
        """Test Sensitive field type with null input.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: Optional[Sensitive]

        config_data = {'my_sensitive_field': None}
        tcex = playbook_app(config_data=config_data).tcex
        tcex.inputs.add_model(PytestModel)

        assert tcex.inputs.data.my_sensitive_field is None

    @staticmethod
    def test_field_type_sensitive_input_blank_binary_not_allowed(playbook_app: 'MockApp'):
        """Test Sensitive field type with blank binary input.

        Bad initializer value. Sensitive only takes String and Binary values.

        Args:
            playbook_app (fixture): An instance of MockApp.
        """

        class PytestModel(BaseModel):
            """Test Model for Inputs"""

            my_sensitive_field: Sensitive

        config_data = {'my_sensitive_field': []}
        app = playbook_app(config_data=config_data)
        tcex = app.tcex
        with pytest.raises(ValidationError) as exc_info:
            tcex.inputs.add_model(PytestModel)

        assert 'Sensitive Type expects String or Bytes values' in str(exc_info.value)



