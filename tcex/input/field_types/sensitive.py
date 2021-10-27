"""Sensitive Field Type"""
# TODO: [high] update docstrings
# standard library
import logging
from typing import Any, Callable, Dict, Optional

# get tcex logger
logger = logging.getLogger('tcex')


def _update_not_none(mapping: Dict[Any, Any], **update: Any) -> None:
    """."""
    mapping.update({k: v for k, v in update.items() if v is not None})


# TODO: [low] do we need all these methods (e.g., __repr__, __len__)
class Sensitive:
    """Field Type to hold sensitive data."""

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    _optional = False

    def __init__(self, value: str):
        """Initialize the Sensitive object."""
        if isinstance(value, Sensitive):
            self._sensitive_value = value.value
        else:
            self._sensitive_value = value

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    def __len__(self) -> int:
        """Return the length of the sensitive value."""
        return len(self._sensitive_value)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        """."""
        _update_not_none(
            field_schema,
            type='string',
            writeOnly=True,
            format='password',
            minLength=cls.min_length,
            maxLength=cls.max_length,
        )

    def __repr__(self) -> str:
        """."""
        return f'''Sensitive('{self}')'''

    def __str__(self) -> str:
        """Return the value masked.

        If App is running in > DEBUG logging level and the sensitive data is greater
        than X, then show the first and last character of the value. This is very
        helpful in debugging App where the incorrect creds could have been passed.
        """
        if self._sensitive_value and logger.getEffectiveLevel() >= 10:  # DEBUG
            if isinstance(self.value, str) and len(self.value) >= 10:
                return f'''{self.value[:1]}{'*' * 4}{self.value[-1:]}'''
        return '**********' if self.value else ''

    @classmethod
    def _validate(cls, value: Any) -> 'Sensitive':
        """Pydantic validate method."""
        if isinstance(value, cls):
            return value

        if not isinstance(value, (bytes, str)):
            raise ValueError(
                f'Sensitive Type expects String or Bytes values, received: {type(value)}'
            )

        if (value == '' or value == b'') and not cls._optional:
            raise ValueError(
                f'Sensitive value may not be empty. Consider using Optional field variant '
                'definition if empty values are necessary.'
            )

        return cls(value)

    @property
    def value(self) -> str:
        """Return the actual value."""
        return self._sensitive_value


class SensitiveOptional(Sensitive):
    """Optional Field Type to hold sensitive data."""
    _optional = True
