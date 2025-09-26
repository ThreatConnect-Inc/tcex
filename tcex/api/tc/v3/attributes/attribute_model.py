"""TcEx Framework Module"""

from datetime import datetime

from pydantic import BaseModel, Field

from tcex.util import Util


class AttributeModel(
    BaseModel,
    title='Attribute Model',
    alias_generator=Util().snake_to_camel,
    extra='allow',
    validate_assignment=True,
):
    """Attribute Model"""

    date_added: datetime | None = Field(
        None,
        frozen=True,
        description='The date and time that the Attribute was added.',
        # TODO: @bsummers-tc
        # read_only=True,
        title='dateAdded',
    )
    id: int = Field(
        ...,
        frozen=True,
        description='The **attribute** Id.',
        # TODO: @bsummers-tc
        # read_only=True,
        title='id',
    )
    last_modified: datetime | None = Field(
        None,
        frozen=True,
        description='The date and time that the Attribute was last modified.',
        # TODO: @bsummers-tc
        # read_only=True,
        title='lastUsed',
    )
    type: str = Field(
        ...,
        description='The defined attribute type.',
        max_length=255,
        min_length=0,
        # TODO: @bsummers-tc
        # read_only=False,
        title='type',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    value: str | None = Field(
        ...,
        description='The attribute value.',
        # TODO: @bsummers-tc
        # read_only=True,
        title='value',
        json_schema_extra={'methods': ['POST', 'PUT']},
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
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
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
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# add forward references
AttributeData.model_rebuild()
AttributeModel.model_rebuild()
AttributesModel.model_rebuild()
