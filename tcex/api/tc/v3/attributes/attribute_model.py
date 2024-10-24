"""TcEx Framework Module"""

# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.util import Util


class AttributeModel(
    BaseModel,
    title='Attribute Model',
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Attribute Model"""

    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was added.',
        read_only=True,
        title='dateAdded',
    )
    id: int = Field(
        None,
        allow_mutation=False,
        description='The **attribute** Id.',
        read_only=True,
        title='id',
    )
    last_modified: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was last modified.',
        read_only=True,
        title='lastUsed',
    )
    type: str = Field(
        None,
        description='The defined attribute type.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=0,
        read_only=False,
        title='type',
    )
    value: str | None = Field(
        None,
        description='The attribute value.',
        methods=['POST', 'PUT'],
        read_only=True,
        title='value',
    )


class AttributeData(
    BaseModel,
    title='Attribute Data',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Attribute Data"""

    data: AttributeModel | None = Field(
        None,
        description='The data for the Attribute.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AttributesModel(
    BaseModel,
    title='Attributes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Attributes Model"""

    data: list[AttributeModel] | None = Field(
        [],
        description='The data for the Attribute.',
        methods=['POST', 'PUT'],
        title='data',
    )


# add forward references
AttributeData.update_forward_refs()
AttributeModel.update_forward_refs()
AttributesModel.update_forward_refs()
