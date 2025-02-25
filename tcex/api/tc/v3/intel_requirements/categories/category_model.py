"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class CategoryModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Category Model',
    validate_assignment=True,
):
    """Category Model"""

    _associated_type = PrivateAttr(default=False)
    _cm_type = PrivateAttr(default=False)
    _shared_type = PrivateAttr(default=False)
    _staged = PrivateAttr(default=False)

    description: str | None = Field(
        None,
        description='The description of the subtype/category.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='description',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: str | None = Field(
        None,
        description='The details of the subtype/category.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
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
        methods=['POST', 'PUT'],
        title='data',
    )


class CategoriesModel(
    BaseModel,
    title='Categories Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Categories Model"""

    _mode_support = PrivateAttr(default=False)

    data: list[CategoryModel] | None = Field(
        [],
        description='The data for the Categories.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


# add forward references
CategoryDataModel.update_forward_refs()
CategoryModel.update_forward_refs()
CategoriesModel.update_forward_refs()
