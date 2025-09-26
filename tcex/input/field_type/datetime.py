"""TcEx Framework Module"""

from typing import Any

import arrow
from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema

from tcex.input.field_type.exception import InvalidInput
from tcex.util import Util


class DateTime(arrow.Arrow):
    """Datetime (Arrow) Field Type"""

    @classmethod
    def _validate(cls, value: Any, info: core_schema.ValidationInfo) -> arrow.Arrow:
        """Pydantic validate method."""
        field_name = info.field_name or '--unknown--'
        try:
            return Util.any_to_datetime(value)
        except RuntimeError as ex:
            raise InvalidInput(field_name=field_name, error=str(ex)) from ex

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        """Run validators / modifiers on input."""
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.any_schema(),
            field_name=handler.field_name,
        )
