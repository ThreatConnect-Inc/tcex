"""TcEx Framework Module"""

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class FileOccurrenceModel(
    V3ModelABC,
    title='File Occurrence Model',
    extra='allow',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """File Occurrences Model"""

    date: datetime | None = Field(
        None,
        json_schema_extra={'methods': ['POST']},
        title='date',
    )
    file_name: str | None = Field(
        None,
        json_schema_extra={'methods': ['POST', 'PUT']},
        title='fileName',
    )
    path: str | None = Field(
        None,
        json_schema_extra={'methods': ['POST', 'PUT']},
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

    _mode_support: bool = PrivateAttr(default=True)

    count: int | None = Field(None, description='The number of occurrences.')

    data: list[FileOccurrenceModel] | None = Field(
        [],
        json_schema_extra={'methods': ['POST', 'PUT']},
        title='data',
    )

    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        json_schema_extra={'methods': ['POST', 'PUT']},
        title='append',
    )


FileOccurrenceModel.model_rebuild()
FileOccurrencesModel.model_rebuild()
