"""not_in argument validator."""
# standard library
from typing import Any, List

from .validation_exception import ValidationError


def not_in(invalid_values: List[Any]):
    """Validate a String is in not equal to any of the values in invalid_values.

    Allowed argument types: String, StringArray, TCEntity, TCEntityArray


    Params:
        invalid_values (List[Any]): List of values that the argument value cannot be.
        **kwargs ():
            strip (Bool): call .strip() on the argument value

    Returns:
        A validator function that can be used in the validators argument to @ReadArg.
    """

    def _validate(value, arg_name):
        if value in invalid_values:
            formatted_values = ', '.join(
                [f'"{n}"' if isinstance(n, str) else str(n) for n in invalid_values]
            )

            raise ValidationError(f'{arg_name} cannot be in [{formatted_values}]')

    return _validate
