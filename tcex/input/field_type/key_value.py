"""TcEx Framework Module"""

# standard library
from typing import ForwardRef

# third-party
from pydantic import BaseModel, validator
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_type.binary import Binary
from tcex.input.field_type.exception import InvalidEmptyValue
from tcex.input.field_type.sensitive import Sensitive
from tcex.input.field_type.string import String
from tcex.input.field_type.tc_entity import TCEntity

KeyValue = ForwardRef('KeyValue')  # type: ignore


# pylint: disable=no-self-argument
class KeyValue(BaseModel):
    """Model for KeyValue Input."""

    key: str
    type: str | None
    value: (
        list[KeyValue]  # SELF-REFERENCE
        | KeyValue  # SELF-REFERENCE
        | list[TCEntity]
        | TCEntity
        | list[String]
        | String
        | list[Binary]
        | Binary
        | Sensitive
    )

    @validator('key')
    def non_empty_string(cls, value: str, field: ModelField) -> str:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    class Config:
        """Model Config"""

        validate_assignment = True


KeyValue.update_forward_refs()


def key_value(allow_none=False):
    """Return configured instance of KeyValue model."""
    key_value_model = KeyValue
    if allow_none is True:

        class _KeyValue(KeyValue):
            value: (
                list[KeyValue]
                | KeyValue
                | list[TCEntity]
                | TCEntity
                | list[String]
                | String
                | list[Binary]
                | Binary
                | Sensitive
                | None
            )

        key_value_model = _KeyValue
    return key_value_model
