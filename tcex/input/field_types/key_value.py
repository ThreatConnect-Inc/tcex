"""KeyValue Playbook Type"""
# standard library
from typing import TYPE_CHECKING, Any, Dict, Optional

# third-party
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_types.exception import InvalidEmptyValue

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


# pylint: disable=no-self-argument, no-self-use
class KeyValue(BaseModel):
    """Model for KeyValue Input."""

    key: str
    type: Optional[str]
    value: Any

    @validator('key')
    def non_empty_string(cls, value: str, field: 'ModelField') -> Dict[str, Any]:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    class Config:
        """Model Config"""

        validate_assignment = True
