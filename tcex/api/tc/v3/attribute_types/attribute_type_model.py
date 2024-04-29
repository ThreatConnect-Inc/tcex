"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class AttributeTypeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='AttributeType Model',
    validate_assignment=True,
):
    """Attribute_Type Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    allow_markdown: bool = Field(
        None,
        description='Flag that enables markdown feature in the attribute value field.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='allowMarkdown',
    )
    description: str | None = Field(
        None,
        description='The description of the attribute type.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='description',
    )
    error_message: str | None = Field(
        None,
        description='The error message displayed.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='errorMessage',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    max_size: int | None = Field(
        None,
        description='The maximum size of the attribute value.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='maxSize',
    )
    name: str | None = Field(
        None,
        description='The name of the attribute type.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    validation_rule: dict | None = Field(
        None,
        description='The validation rule that governs the attribute value.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='validationRule',
    )


class AttributeTypeDataModel(
    BaseModel,
    title='AttributeType Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Attribute_Types Data Model"""

    data: list[AttributeTypeModel] | None = Field(
        [],
        description='The data for the AttributeTypes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AttributeTypesModel(
    BaseModel,
    title='AttributeTypes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Attribute_Types Model"""

    _mode_support = PrivateAttr(False)

    data: list[AttributeTypeModel] | None = Field(
        [],
        description='The data for the AttributeTypes.',
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
AttributeTypeDataModel.update_forward_refs()
AttributeTypeModel.update_forward_refs()
AttributeTypesModel.update_forward_refs()
