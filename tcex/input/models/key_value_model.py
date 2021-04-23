"""KeyValue Model"""
# standard library
from typing import Any

# third-party
from pydantic import BaseModel


class KeyValueModel(BaseModel):
    """Model for KeyValue Input."""

    key: str
    value: Any

    class Config:
        """Model Config"""

        validate_assignment = True
