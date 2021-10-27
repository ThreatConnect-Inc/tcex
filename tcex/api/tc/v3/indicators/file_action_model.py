"""File Actions Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel

# first-party
from tcex.utils import Utils


class FileActionModel(
    BaseModel,
    title='File Actions Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """File Actions Model"""

    action: Optional[str]
