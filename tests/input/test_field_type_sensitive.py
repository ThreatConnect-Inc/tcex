"""Testing TcEx Input module field types."""
# standard library
from typing import TYPE_CHECKING

# third-party
from pydantic import BaseModel

# first-party
from tcex.input.field_types import Sensitive

if TYPE_CHECKING:
    from ..mock_app import MockApp


class TestInputsFieldTypeSensitive:
    """Test TcEx Inputs Config."""

    @staticmethod
    def test_field_type_sensitive(playbook_app: 'MockApp'):
        """Test BinaryArray field type with string input.

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
