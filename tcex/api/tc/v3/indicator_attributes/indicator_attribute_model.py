"""Indicator_Attribute / Indicator_Attributes Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

# json-encoder
json_encoders = {datetime: lambda v: v.isoformat()}


class IndicatorAttributesModel(
    BaseModel,
    title='IndicatorAttributes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Indicator_Attributes Model"""

    data: Optional[List['IndicatorAttributeModel']] = Field(
        [],
        description='The data for the IndicatorAttributes.',
        methods=['POST', 'PUT'],
        title='data',
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
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='IndicatorAttribute Model',
    validate_assignment=True,
    json_encoders=json_encoders,
):
    """Indicator_Attribute Model"""

    # slot attributes are not added to dict()/json()
    __slot__ = ('_privates_',)

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(**kwargs)
        super().__setattr__('_privates_', {'_modified_': 0})

    def __setattr__(self, name, value):
        """Update modified property on any update."""
        super().__setattr__('_privates_', {'_modified_': self.privates.get('_modified_', 0) + 1})
        super().__setattr__(name, value)

    @property
    def modified(self):
        """Return int value of modified (> 0 means modified)."""
        return self._privates_.get('_modified_', 0)

    @property
    def privates(self):
        """Return privates dict."""
        return self._privates_

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
        description='The date and time that the Attribute was first created.',
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
    indicator_id: Optional[int] = Field(
        None,
        description='Indicator associated with attribute.',
        methods=['POST'],
        read_only=False,
        title='indicatorId',
        updatable=False,
    )
    last_modified: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was last modified.',
        read_only=True,
        title='lastModified',
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
        updatable=False,
    )
    value: Optional[str] = Field(
        None,
        description='Attribute value.',
        methods=['POST', 'PUT'],
        min_length=1,
        read_only=False,
        title='value',
    )

    @validator('created_by', always=True)
    def _validate_created_by(cls, v):
        if not v:
            return UserModel()
        return v


# first-party
from tcex.api.tc.v3.security.users.user_model import UserModel

# add forward references
IndicatorAttributeDataModel.update_forward_refs()
IndicatorAttributeModel.update_forward_refs()
IndicatorAttributesModel.update_forward_refs()
