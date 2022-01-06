"""Valid Values Field Type"""
# standard library
from typing import TYPE_CHECKING, Callable

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.input.field_types.exception import InvalidInput, InvalidType

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


class EditChoice(str):
    """EditChoice Field Type

    Used for Apps Param types:
    * EditChoice (pre-defined values)

    Unsupported:
    * Magic Variables (e.g. ${OWNERS})
    * EditChoice (dynamic values supported)
    """

    ij = InstallJson()

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Run validators / modifiers on input."""
        yield cls.validate_type
        yield cls.modifier_strip
        yield cls.validate_valid_values

    @classmethod
    def modifier_strip(cls, value: str) -> str:
        """Modify value, stripping whitespace."""
        return value.strip()

    @classmethod
    def validate_type(cls, value: str, field: 'ModelField') -> str:
        """Raise exception if value is not a String type."""
        if not isinstance(value, str):
            raise InvalidType(
                field_name=field.name, expected_types='(str)', provided_type=type(value)
            )
        return value

    @classmethod
    def validate_valid_values(cls, value: str, field: 'ModelField') -> str:
        """Raise exception if value is not a String type."""
        _valid_values = cls.ij.model.get_param(field.name).valid_values or []
        for vv in _valid_values:
            if vv.lower() == value.lower():
                value = vv
                break
        else:
            raise InvalidInput(
                field_name=field.name,
                error=f'provided value {value} is not a valid value {_valid_values}',
            )
        return value
