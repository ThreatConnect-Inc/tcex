"""File Occurrences Model"""
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class FileOccurrencesModel(
    BaseModel,
    title='File Occurrences Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Data Model"""

    _mode_support = PrivateAttr(True)

    count: Optional[int] = Field(None, description='The number of occurrences.')

    data: Optional[List['FileOccurrenceModel']] = Field(
        [],
        methods=['POST', 'PUT'],
        title='data',
    )

    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class FileOccurrenceModel(
    V3ModelABC,
    title='File Occurrence Model',
    extra=Extra.allow,
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Model"""

    date: Optional[datetime] = Field(
        None,
        methods=['POST', 'PUT'],
        title='date',
    )
    file_name: Optional[str] = Field(
        None,
        methods=['POST', 'PUT'],
        title='fileName',
    )
    path: Optional[str] = Field(
        None,
        methods=['POST', 'PUT'],
        title='path',
    )
    id: Optional[int] = Field(
        None,
        title='id',
    )


FileOccurrenceModel.update_forward_refs()
FileOccurrencesModel.update_forward_refs()
