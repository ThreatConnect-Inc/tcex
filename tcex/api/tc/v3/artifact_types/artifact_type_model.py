"""Artifact_Type / Artifact_Types Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class ArtifactTypesModel(
    BaseModel,
    title='ArtifactTypes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Artifact_Types Model"""

    data: Optional[List['ArtifactTypeModel']] = Field(
        [],
        description='The data for the ArtifactTypes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class ArtifactTypeDataModel(
    BaseModel,
    title='ArtifactType Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Artifact_Types Data Model"""

    data: Optional[List['ArtifactTypeModel']] = Field(
        [],
        description='The data for the ArtifactTypes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class ArtifactTypeModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='ArtifactType Model',
    validate_assignment=True,
):
    """Artifact_Type Model"""

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

    data_type: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **data type** for the Artifact_Type.',
        read_only=True,
        title='dataType',
    )
    derived_link: bool = Field(
        None,
        allow_mutation=False,
        description='The **derived link** for the Artifact_Type.',
        read_only=True,
        title='derivedLink',
    )
    description: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description** for the Artifact_Type.',
        read_only=True,
        title='description',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    intel_type: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **intel type** for the Artifact_Type.',
        read_only=True,
        title='intelType',
    )
    name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **name** for the Artifact_Type.',
        read_only=True,
        title='name',
    )


# add forward references
ArtifactTypeDataModel.update_forward_refs()
ArtifactTypeModel.update_forward_refs()
ArtifactTypesModel.update_forward_refs()
