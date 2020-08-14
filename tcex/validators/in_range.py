"""in_range argument validator."""
from .validation_exception import ValidationError


def in_range(min: float, max: float, **kwargs):  # pylint: disable=redefined-builtin
    """Validate a value is in the range min <= value <= max.

    For a StringArray, validates that every element in the array is min <= value <= max.

    Allowed argument types: String, StringArray


    Params:
        min (float): the minimum valid value for the argument
        max (float): the maximum valid value for the argument
        allow_none (bool): If none or '' values are ok in a StringArray. default: False

    Returns:
        A validator function that can be used in the validators argument to @ReadArg.
    """

    def _validate(value, arg_name):
        allow_none = kwargs.get('allow_none', False)

        if not isinstance(value, list):
            value = [value]

        for v in value:
            if (v is None or v == '') and allow_none:
                continue

            if not min <= v <= max:
                raise ValidationError(f'{arg_name} is not between {min} and {max}.')

    return _validate
