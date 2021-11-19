"""Security_Label / Security_Labels Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class SecurityLabelsModel(
    BaseModel,
    title='SecurityLabels Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Security_Labels Model"""

    _mode_support = PrivateAttr(True)

    data: Optional[List['SecurityLabelModel']] = Field(
        [],
        description='The data for the SecurityLabels.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class SecurityLabelDataModel(
    BaseModel,
    title='SecurityLabel Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Security_Labels Data Model"""

    data: Optional[List['SecurityLabelModel']] = Field(
        [],
        description='The data for the SecurityLabels.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SecurityLabelModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='SecurityLabel Model',
    validate_assignment=True,
):
    """Security_Label Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(True)
    _staged = PrivateAttr(False)

    color: Optional[str] = Field(
        None,
        description='Color of the security label.',
        methods=['POST', 'PUT'],
        max_length=10,
        min_length=1,
        read_only=False,
        title='color',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the label was added.',
        read_only=True,
        title='dateAdded',
    )
    description: Optional[str] = Field(
        None,
        description='Description of the security label.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='description',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        description='Name of the security label.',
        methods=['POST', 'PUT'],
        max_length=50,
        min_length=1,
        read_only=False,
        title='name',
    )
    owner: Optional[str] = Field(
        None,
        description='The name of the Owner of the Label.',
        methods=['POST'],
        read_only=False,
        title='owner',
    )


# add forward references
SecurityLabelDataModel.update_forward_refs()
SecurityLabelModel.update_forward_refs()
SecurityLabelsModel.update_forward_refs()
