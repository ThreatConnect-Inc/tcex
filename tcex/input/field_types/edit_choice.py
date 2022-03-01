"""Valid Values Field Type"""
# standard library
from typing import TYPE_CHECKING, Callable, Dict, Optional

# first-party
from tcex.api.tc.utils.threat_intel_utils import ThreatIntelUtils
from tcex.app_config.install_json import InstallJson
from tcex.input.field_types.exception import InvalidEmptyValue, InvalidInput, InvalidType
from tcex.pleb.none_model import NoneModel
from tcex.pleb.registry import registry

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

    _allow_additional = False
    _value_transformations = None

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
        if value == '':
            raise InvalidEmptyValue(field.name)

        ij = InstallJson()
        param = ij.model.get_param(field.name)

        # TODO: [high] figure out a better way ...
        if isinstance(param, NoneModel):
            # for a multichoice input field, pydantic prefixes the name with an underscore,
            # this breaks the lookup based on the "name" field in the install.json. Strip
            # the underscore to get the correct param name.
            param = ij.model.get_param(field.name.lstrip('_'))

        ti_utils = ThreatIntelUtils(registry.session_tc)
        _valid_values = ti_utils.resolve_variables(param.valid_values or [])
        for vv in _valid_values:
            if vv.lower() == value.lower():
                value = vv
                break
        else:
            if cls._allow_additional is False:
                raise InvalidInput(
                    field_name=field.name,
                    error=f'provided value {value} is not a valid value {_valid_values}',
                )

        if isinstance(cls._value_transformations, dict):
            value = cls._value_transformations.get(value, value)

        return value


def edit_choice(
    allow_additional: bool = False, value_transformations: Optional[Dict[str, str]] = None
) -> type:
    """Return configured instance of String.

    :param allow_additional: Denotes whether this field will allow values that are not found in
    the field's valid values list in the install.json.
    :param value_transformations: dictionary that dictates how a choice should be transformed.
    Dictionary keys should be the field's valid values as defined in the install.json. Example:

    value_transformations: {'my_choice': 'My Choice'}

    If this field were to be initialized with 'my_choice', then the final value found in the input
    model would be 'My Choice'.
    """
    namespace = dict(
        _value_transformations=value_transformations,
        _allow_additional=allow_additional,
    )
    return type('CustomEditChoice', (EditChoice,), namespace)
