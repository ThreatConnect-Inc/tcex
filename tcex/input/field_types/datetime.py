"""Datetime (Arrow) Field Type"""
# standard library
from typing import TYPE_CHECKING, Any, Callable

# third-party
import arrow

# first-party
from tcex.input.field_types.exception import InvalidInput
from tcex.utils import Utils

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


class DateTime(arrow.Arrow):
    """Datetime (Arrow) Field Type"""

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    @classmethod
    def _validate(cls, value: Any, field: 'ModelField') -> 'arrow.Arrow':
        """Pydantic validate method."""
        try:
            return Utils.any_to_datetime(value)
        except RuntimeError as ex:
            raise InvalidInput(field_name=field.name, error=str(ex)) from ex
