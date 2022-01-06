"""Choice Field Type"""
# standard library
from typing import Callable

# first-party
from tcex.input.field_types.edit_choice import EditChoice


class Choice(EditChoice):
    """Choice Field Type"""

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Run validators / modifiers on input."""
        yield cls.modifier_select
        yield from super().__get_validators__()

    @classmethod
    def modifier_select(cls, value: str) -> str:
        """Modify value if -- Select -- option is selected.

        Job Apps: If not selection None is sent.
        PB Apps: '-- Select --' has to be added to validValues by developer.
        """
        if value == '-- Select --':
            value = None
        return value
