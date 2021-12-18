"""KeyValue Playbook Type"""
# standard library
from typing import Any, Optional

# third-party
from pydantic import BaseModel, validator


# pylint: disable=no-self-argument, no-self-use
class KeyValue(BaseModel):
    """Model for KeyValue Input."""

    key: str
    type: Optional[str]
    value: Any

    @validator('key')
    def non_empty_string(cls, v):
        """Validate that the value is a non-empty string."""
        if v == '':
            raise ValueError('Empty value is not allowed.')
        return v

    class Config:
        """Model Config"""

        validate_assignment = True
