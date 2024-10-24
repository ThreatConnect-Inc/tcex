"""TcEx Framework Module"""

# standard library
from collections.abc import Generator
from typing import Any

# third-party
import arrow
from pydantic.fields import ModelField

# first-party
from tcex.input.field_type.exception import InvalidInput
from tcex.util import Util


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
            return Util.any_to_datetime(value)
        except RuntimeError as ex:
            raise InvalidInput(field_name=field.name, error=str(ex)) from ex
