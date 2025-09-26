"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class AttributeTypeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='AttributeType Model',
    validate_assignment=True,
):
    """Attribute_Type Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    allow_markdown: bool | None = Field(
        default=None,
        description='Flag that enables markdown feature in the attribute value field.',
        title='allowMarkdown',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    description: str | None = Field(
        default=None,
        description='The description of the attribute type.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    error_message: str | None = Field(
        default=None,
        description='The error message displayed.',
        title='errorMessage',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    max_size: int | None = Field(
        default=None,
        description='The maximum size of the attribute value.',
        title='maxSize',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    name: str | None = Field(
        default=None,
        description='The name of the attribute type.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    validation_rule: dict | None = Field(
        default=None,
        description='The validation rule that governs the attribute value.',
        title='validationRule',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
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
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class AttributeTypesModel(
    BaseModel,
    title='AttributeTypes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Attribute_Types Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[AttributeTypeModel] | None = Field(
        [],
        description='The data for the AttributeTypes.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
AttributeTypeDataModel.model_rebuild()
AttributeTypeModel.model_rebuild()
AttributeTypesModel.model_rebuild()
