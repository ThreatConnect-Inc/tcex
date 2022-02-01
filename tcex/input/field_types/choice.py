"""Choice Field Type"""
# standard library
from typing import Callable, Dict, Optional

# first-party
from tcex.input.field_types.edit_choice import EditChoice
from tcex.input.field_types.exception import InvalidInput


class Choice(EditChoice):
    """Choice Field Type"""

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Run validators / modifiers on input."""
        yield from super().__get_validators__()
        yield cls.modifier_select

    @classmethod
    def modifier_select(cls, value: str, field) -> str:
        """Modify value if -- Select -- option is selected.

        Job Apps: If not selection None is sent.
        PB Apps: '-- Select --' has to be added to validValues by developer.
        """
        if value == '-- Select --':
            if field.allow_none is False:
                raise InvalidInput(field.name, f'{value} is not a valid choice.')
            value = None

        return value


def choice(value_transformations: Optional[Dict[str, str]] = None) -> type:
    """Return configured instance of String.

    :param value_transformations: dictionary that dictates how a choice should be transformed.
    Dictionary keys should be the field's valid values as defined in the install.json. Example:

    value_transformations: {'my_choice': 'My Choice'}

    If this field were to be initialized with 'my_choice', then the final value found in the input
    model would be 'My Choice'.
    """
    namespace = dict(_value_transformations=value_transformations)
    return type('CustomChoice', (Choice,), namespace)
