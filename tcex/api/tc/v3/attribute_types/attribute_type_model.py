"""Attribute_Type / Attribute_Types Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class AttributeTypesModel(
    BaseModel,
    title='AttributeTypes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Attribute_Types Model"""

    _mode_support = PrivateAttr(False)

    data: Optional[List['AttributeTypeModel']] = Field(
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


class AttributeTypeDataModel(
    BaseModel,
    title='AttributeType Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Attribute_Types Data Model"""

    data: Optional[List['AttributeTypeModel']] = Field(
        [],
        description='The data for the AttributeTypes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AttributeTypeModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='AttributeType Model',
    validate_assignment=True,
):
    """Attribute_Type Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )


# add forward references
AttributeTypeDataModel.update_forward_refs()
AttributeTypeModel.update_forward_refs()
AttributeTypesModel.update_forward_refs()
