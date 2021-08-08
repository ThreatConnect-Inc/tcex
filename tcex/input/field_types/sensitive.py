"""."""
# TODO: [high] update docstrings
# standard library
from typing import Any, Callable, Dict, Optional


def _update_not_none(mapping: Dict[Any, Any], **update: Any) -> None:
    """."""
    mapping.update({k: v for k, v in update.items() if v is not None})


# TODO: [low] do we need all these methods (e.g., __repr__, __len__)
class Sensitive:
    """Field Type to hold sensitive data."""

    min_length: Optional[int] = None
    max_length: Optional[int] = None

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

    @classmethod
    def __get_validators__(cls) -> 'Callable':
        """Define one or more validators for Pydantic custom type."""
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> 'Sensitive':
        """."""
        if isinstance(value, cls):
            return value
        return cls(value)

    def __init__(self, value: str):
        """."""
        self._sensitive_value = value

    def __repr__(self) -> str:
        """."""
        return f'''Sensitive('{self}')'''

    def __str__(self) -> str:
        """."""
        return '**********' if self._sensitive_value else ''

    def __len__(self) -> int:
        """."""
        return len(self._sensitive_value)

    @property
    def value(self) -> str:
        """."""
        return self._sensitive_value
