"""TcEx Framework Module"""

from typing import Any

from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic.dataclasses import dataclass
from pydantic_core import core_schema

from tcex.app.config.install_json import InstallJson
from tcex.input.field_type.edit_choice import EditChoice
from tcex.input.field_type.exception import InvalidInput


@dataclass(frozen=True, init=False)
class Choice(EditChoice):
    """Choice Field Type"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.ChainSchema:
        """Run validators / modifiers on input."""

        # Get parent class _validate method
        parent_validate = super()._validate  # type: ignore[misc]

        base_validate = core_schema.with_info_plain_validator_function(
            function=parent_validate, field_name=handler.field_name
        )
        modifier_select = core_schema.with_info_plain_validator_function(
            function=cls.modifier_select, field_name=handler.field_name
        )
        return core_schema.chain_schema(
            [
                base_validate,
                modifier_select,
            ]
        )

    @classmethod
    def modifier_select(cls, value: str, info: core_schema.ValidationInfo) -> str | None:
        """Modify value if -- Select -- option is selected.

        Job Apps: If not selection None is sent.
        PB Apps: '-- Select --' has to be added to validValues by developer.
        """
        if info.field_name is None:
            return value

        _value = value
        if _value == '-- Select --':
            ij = InstallJson()
            param = ij.model.get_param(info.field_name)

            if param is None:
                ex_msg = f'Install.json does not contain a parameter for {info.field_name}.'
                raise ValueError(ex_msg)

            if param.required is True:
                raise InvalidInput(info.field_name, f'{_value} is not a valid choice.')
            _value = None

        return _value


def choice(value_transformations: dict[str, str] | None = None) -> type[Choice]:
    """Return configured instance of String.

    :param value_transformations: dictionary that dictates how a choice should be transformed.
    Dictionary keys should be the field's valid values as defined in the install.json. Example:

    value_transformations: {'my_choice': 'My Choice'}

    If this field were to be initialized with 'my_choice', then the final value found in the input
    model would be 'My Choice'.
    """
    namespace = {'_value_transformations': value_transformations}
    return type('CustomChoice', (Choice,), namespace)
