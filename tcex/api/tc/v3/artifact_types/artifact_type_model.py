"""Artifact_Type / Artifact_Types Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class ArtifactTypesModel(
    BaseModel,
    title='ArtifactTypes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Artifact_Types Model"""

    _mode_support = PrivateAttr(False)

    data: Optional[List['ArtifactTypeModel']] = Field(
        [],
        description='The data for the ArtifactTypes.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
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
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='ArtifactType Model',
    validate_assignment=True,
):
    """Artifact_Type Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

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
