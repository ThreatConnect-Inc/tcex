"""TCEntity Playbook Type"""
# standard library
from typing import Dict, Optional

# third-party
from pydantic import BaseModel, Extra, validator


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
    def non_empty_string(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate that the value is a non-empty string."""
        if isinstance(v, str) and v.replace(' ', '') == '':  # None value are automatically covered
            raise ValueError('Empty value is not allowed.')

        if v == '':  # None value are automatically covered
            raise ValueError('Empty value is not allowed.')
        return v

    class Config:
        """Model Config"""

        validate_assignment = True
        extra = Extra.allow
