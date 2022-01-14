"""TCEntity Playbook Type"""
# standard library
from typing import TYPE_CHECKING, Dict, Optional

# third-party
from pydantic import BaseModel, Extra, validator

# first-party
from tcex.input.field_types.exception import InvalidEmptyValue

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


# pylint: disable=no-self-argument, no-self-use
class TCEntity(BaseModel):
    """Model for TCEntity Input."""

    id: int
    type: str
    value: str

    # IMPORTANT: confidence and rating values are included only so that, when defined,
    #    they come back as the correct types. They are only intended for Indicator
    #    types and are not guaranteed to be populated.
    confidence: Optional[int]
    rating: Optional[int]

    @validator('id', 'type', 'value')
    def non_empty_string(cls, v: Dict[str, str], field: 'ModelField') -> Dict[str, str]:
        """Validate that the value is a non-empty string."""
        if isinstance(v, str) and v.replace(' ', '') == '':  # None value are automatically covered
            raise InvalidEmptyValue(field_name=field.name)
        return v

    class Config:
        """Model Config"""

        extra = Extra.allow
        validate_assignment = True
