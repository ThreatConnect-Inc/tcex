"""Indicator_Attribute / Indicator_Attributes Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class IndicatorAttributesModel(
    BaseModel,
    title='IndicatorAttributes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Indicator_Attributes Model"""

    _mode_support = PrivateAttr(True)

    data: Optional[List['IndicatorAttributeModel']] = Field(
        [],
        description='The data for the IndicatorAttributes.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class IndicatorAttributeDataModel(
    BaseModel,
    title='IndicatorAttribute Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Indicator_Attributes Data Model"""

    data: Optional[List['IndicatorAttributeModel']] = Field(
        [],
        description='The data for the IndicatorAttributes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class IndicatorAttributeModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='IndicatorAttribute Model',
    validate_assignment=True,
):
    """Indicator_Attribute Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    created_by: Optional['UserModel'] = Field(
        None,
        allow_mutation=False,
        description='The **created by** for the Indicator_Attribute.',
        read_only=True,
        title='createdBy',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    default: bool = Field(
        None,
        description=(
            'A flag indicating that this is the default attribute of its type within the object. '
            'Only applies to certain attribute and data types.'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='default',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    indicator: Optional['IndicatorModel'] = Field(
        None,
        allow_mutation=False,
        description='Details of indicator associated with attribute.',
        read_only=True,
        title='indicator',
    )
    indicator_id: Optional[int] = Field(
        None,
        description='Indicator associated with attribute.',
        methods=['POST'],
        read_only=False,
        title='indicatorId',
    )
    last_modified: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was last modified.',
        read_only=True,
        title='lastModified',
    )
    pinned: bool = Field(
        None,
        description='A flag indicating that the attribute has been noted for importance.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='pinned',
    )
    security_labels: Optional['SecurityLabelsModel'] = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityLabels',
    )
    source: Optional[str] = Field(
        None,
        description='The attribute source.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='source',
    )
    type: Optional[str] = Field(
        None,
        description='The attribute type.',
        methods=['POST'],
        read_only=False,
        title='type',
    )
    value: Optional[str] = Field(
        None,
        description='The attribute value.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='value',
    )

    @validator('indicator', always=True)
    def _validate_indicator(cls, v):
        if not v:
            return IndicatorModel()
        return v

    @validator('security_labels', always=True)
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()
        return v

    @validator('created_by', always=True)
    def _validate_user(cls, v):
        if not v:
            return UserModel()
        return v


# first-party
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel

# add forward references
IndicatorAttributeDataModel.update_forward_refs()
IndicatorAttributeModel.update_forward_refs()
IndicatorAttributesModel.update_forward_refs()
