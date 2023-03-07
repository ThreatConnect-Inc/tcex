"""Datetime (Arrow) Field Type"""
# standard library
from collections.abc import Generator
from typing import Any

# third-party
import arrow
from pydantic.fields import ModelField

# first-party
from tcex.input.field_types.exception import InvalidInput
from tcex.utils import Utils


class DateTime(arrow.Arrow):
    """Datetime (Arrow) Field Type"""

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    @classmethod
    def _validate(cls, value: Any, field: ModelField) -> arrow.Arrow:
        """Pydantic validate method."""
        try:
            return Utils.any_to_datetime(value)
        except RuntimeError as ex:
            raise InvalidInput(field_name=field.name, error=str(ex)) from ex
