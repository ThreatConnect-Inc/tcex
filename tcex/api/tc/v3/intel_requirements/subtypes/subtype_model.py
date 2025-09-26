"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class SubtypeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Subtype Model',
    validate_assignment=True,
):
    """Subtype Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    description: str | None = Field(
        default=None,
        description='The description of the subtype/category.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The details of the subtype/category.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class SubtypeDataModel(
    BaseModel,
    title='Subtype Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Subtypes Data Model"""

    data: list[SubtypeModel] | None = Field(
        [],
        description='The data for the Subtypes.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class SubtypesModel(
    BaseModel,
    title='Subtypes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Subtypes Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[SubtypeModel] | None = Field(
        [],
        description='The data for the Subtypes.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
SubtypeDataModel.model_rebuild()
SubtypeModel.model_rebuild()
SubtypesModel.model_rebuild()
