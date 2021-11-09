"""Security_Label / Security_Labels Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class SecurityLabelsModel(
    BaseModel,
    title='SecurityLabels Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Security_Labels Model"""

    data: Optional[List['SecurityLabelModel']] = Field(
        [],
        description='The data for the SecurityLabels.',
        methods=['POST', 'PUT'],
        title='data',
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
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='SecurityLabel Model',
    validate_assignment=True,
):
    """Security_Label Model"""

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
        updatable=False,
    )


# add forward references
SecurityLabelDataModel.update_forward_refs()
SecurityLabelModel.update_forward_refs()
SecurityLabelsModel.update_forward_refs()
