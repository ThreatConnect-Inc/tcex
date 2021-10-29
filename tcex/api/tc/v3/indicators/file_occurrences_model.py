"""File Occurrences Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel

# first-party
from tcex.utils import Utils


class FileOccurrencesModel(
    BaseModel,
    title='File Occurrences Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Model"""

    occurrence: Optional[str]
