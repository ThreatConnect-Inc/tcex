"""Declares several transform functions that verify an argument is of a specified type."""
# standard library
from typing import Any

# first-party
from tcex.utils.utils import Utils

from .validation_exception import ValidationError


def _to_type(target_type, **kwargs):
    """Validate that an argument can be cast to a type by calling type(value).

    Accepts either a String or StringArray value.  If A StringArray, validates that every element
    in the array can be cast to the given type.

    Args:
        target_type (class):  type to invoke
        allow_none (bool): If none values are ok. default: False

    Returns:
        A transform function that can be used in the transforms argument to @ReadArg.
    """

    def _transform(value: Any, arg_name: str, label: str):
        """Run transform on input data.

        Args:
            value: The input data to be transformed.
            arg_name: The name of the input arg.
            label: The label displayed to the user.

        Raises:
            ValidationError: raised on validation failure.
        """
        allow_none = kwargs.get('allow_none', False)

        if not isinstance(value, list):
            if (value is None or value == '') and allow_none:
                return value

            try:
                return target_type(value)
            except Exception:
                raise ValidationError(f'"{label}" ({arg_name}) must be a {target_type.__name__}.')

        transformed = []
        for v in value:
            if (v is None or v == '') and allow_none:
                transformed.append(v)
                continue

            try:
                transformed.append(target_type(v))
            except Exception:
                raise ValidationError(f'"{label}" ({arg_name}) must be a {target_type.__name__}.')

        return transformed

    return _transform


def to_int(allow_none=False):
    """Transform an argument into an int

    Allowed argument types: String, StringArray

    Args:
        allow_none (bool): skip any None elements

    Returns:
        A transform function that can be used in the transforms argument to @ReadArg.
    """
    return _to_type(int, allow_none=allow_none)


def to_float(allow_none=False):
    """Transform an argument value into a float.

    Allowed argument types: String, StringArray

    Args:
        allow_none (bool): skip any None elements

    Returns:
        A transform function that can be used in the transforms argument to @ReadArg.
    """
    return _to_type(float, allow_none=allow_none)


def to_bool():
    """Transform an argument value into a bool.

    Allowed argument types: String, StringArray

    Returns:
        A transform function that can be used in the transforms argument to @ReadArg.
    """

    def _validator(value, arg_name, label):  # pylint: disable=unused-argument
        if not isinstance(value, list):
            return Utils.to_bool(value)

        return list([Utils.to_bool(v) for v in value])  # pylint: disable=consider-using-generator

    return _validator
