"""Artifact Type Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils


class ArtifactTypesModel(
    BaseModel,
    title='ArtifactTypes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Artifact Types Model"""

    data: 'Optional[List[ArtifactTypeModel]]' = Field(
        [],
        description='The data for the ArtifactType.',
        methods=['POST', 'PUT'],
        title='data',
    )


class ArtifactTypeData(
    BaseModel,
    title='ArtifactType Data',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True
):
    """Artifact Type Data"""

    data: 'Optional[ArtifactTypeModel]' = Field(
        None,
        description='The data for the ArtifactType.',
        methods=['POST', 'PUT'],
        title='data',
    )


class ArtifactTypeModel(
    BaseModel,
    title='ArtifactType Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True
):
    """Artifact Type Model"""

    data_type: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **data type** for the ArtifactType.',
        read_only=True,
        title='dataType',
    )
    derived_link: bool = Field(
        None,
        allow_mutation=False,
        description='The **derived link** for the ArtifactType.',
        read_only=True,
        title='derivedLink',
    )
    description: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description** for the ArtifactType.',
        read_only=True,
        title='description',
    )
    id: Optional[int] = Field(
        None,
        description='The id of the **Object**.',
        read_only=True,
        title='id',
    )
    intel_type: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **intel type** for the ArtifactType.',
        read_only=True,
        title='intelType',
    )
    name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **name** for the ArtifactType.',
        read_only=True,
        title='name',
    )


# add forward references
ArtifactTypeData.update_forward_refs()
ArtifactTypeModel.update_forward_refs()
ArtifactTypesModel.update_forward_refs()
