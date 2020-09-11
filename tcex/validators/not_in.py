"""not_in argument validator."""
# standard library
from typing import Any, Callable, List

from .validation_exception import ValidationError


def not_in(invalid_values: List[Any]) -> Callable[..., None]:
    """Validate a String is in not equal to any of the values in invalid_values.

    Allowed argument types: String, StringArray, TCEntity, TCEntityArray


    Args:
        invalid_values: List of values that the argument value cannot be.
        **kwargs ():
            strip (bool): call .strip() on the argument value

    Returns:
        A validator function that can be used in the validators argument to @ReadArg.
    """

    def _validate(value: str, arg_name: str, label: str) -> None:
        """Run validation on input data.

        Args:
            value: The input data to validate.
            arg_name: The name of the input arg.
            label: The label displayed to the user.

        Raises:
            ValidationError: raised on validation failure.
        """
        if value in invalid_values:
            formatted_values = ', '.join(
                [f'"{n}"' if isinstance(n, str) else str(n) for n in invalid_values]
            )

            raise ValidationError(f'"{label}" ({arg_name}) cannot be in [{formatted_values}]')

    return _validate
