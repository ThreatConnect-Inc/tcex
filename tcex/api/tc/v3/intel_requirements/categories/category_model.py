"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class CategoryModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Category Model',
    validate_assignment=True,
):
    """Category Model"""

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


class CategoryDataModel(
    BaseModel,
    title='Category Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Categories Data Model"""

    data: list[CategoryModel] | None = Field(
        [],
        description='The data for the Categories.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class CategoriesModel(
    BaseModel,
    title='Categories Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Categories Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[CategoryModel] | None = Field(
        [],
        description='The data for the Categories.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
CategoryDataModel.model_rebuild()
CategoryModel.model_rebuild()
CategoriesModel.model_rebuild()
