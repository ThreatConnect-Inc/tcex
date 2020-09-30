"""in_range argument validator."""
# standard library
from typing import Any, Callable

from .validation_exception import ValidationError


def in_range(
    min: float, max: float, **kwargs  # pylint: disable=redefined-builtin
) -> Callable[..., None]:
    """Validate a value is in the range min <= value <= max.

    For a StringArray, validates that every element in the array is min <= value <= max.

    Allowed argument types: String, StringArray


    Args:
        min: the minimum valid value for the argument
        max: the maximum valid value for the argument
        **kwargs ():
            allow_none (bool): If none or '' values are ok in a StringArray.

    Returns:
        A validator function that can be used in the validators argument to @ReadArg.
    """

    def _validate(value: Any, arg_name: str, label: str) -> None:
        """Run validation on input data.

        Args:
            value: The input data to validate.
            arg_name: The name of the input arg.
            label: The label displayed to the user.

        Raises:
            ValidationError: raised on validation failure.
        """
        allow_none = kwargs.get('allow_none', False)

        if not isinstance(value, list):
            value = [value]

        for v in value:
            if (v is None or v == '') and allow_none:
                continue

            if not min <= v <= max:
                raise ValidationError(f'"{label}" ({arg_name}) is not between {min} and {max}.')

    return _validate
