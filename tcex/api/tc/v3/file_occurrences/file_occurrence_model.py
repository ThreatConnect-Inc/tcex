"""TcEx Framework Module"""

# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class FileOccurrenceModel(
    V3ModelABC,
    title='File Occurrence Model',
    extra=Extra.allow,
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Model"""

    date: datetime | None = Field(
        None,
        methods=['POST', 'PUT'],
        title='date',
    )
    file_name: str | None = Field(
        None,
        methods=['POST', 'PUT'],
        title='fileName',
    )
    path: str | None = Field(
        None,
        methods=['POST', 'PUT'],
        title='path',
    )
    id: int | None = Field(  # type: ignore
        None,
        title='id',
    )


class FileOccurrencesModel(
    BaseModel,
    title='File Occurrences Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Data Model"""

    _mode_support = PrivateAttr(True)

    count: int | None = Field(None, description='The number of occurrences.')

    data: list[FileOccurrenceModel] | None = Field(
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


FileOccurrenceModel.update_forward_refs()
FileOccurrencesModel.update_forward_refs()
