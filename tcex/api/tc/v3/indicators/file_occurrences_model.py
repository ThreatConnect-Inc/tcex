"""File Occurrences Model"""
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Field

# first-party
from tcex.utils import Utils


class FileOccurrencesModel(
    BaseModel,
    title='File Occurrences Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Data Model"""

    count: Optional[int] = Field(None, description='The number of occurrences.')
    data: Optional[List['FileOccurrenceModel']] = Field(
        [],
        methods=['POST', 'PUT'],
        title='data',
    )


class FileOccurrenceModel(
    BaseModel,
    title='File Occurrences Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Model"""

    date: datetime = Field(
        None,
        methods=['POST', 'PUT'],
        title='date',
    )
    file_name: str = Field(
        None,
        methods=['POST', 'PUT'],
        title='fileName',
    )
    id: int = Field(
        None,
        title='id',
    )


FileOccurrenceModel.update_forward_refs()
FileOccurrencesModel.update_forward_refs()
