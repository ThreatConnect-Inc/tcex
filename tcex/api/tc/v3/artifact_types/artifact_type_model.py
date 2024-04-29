"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ArtifactTypeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='ArtifactType Model',
    validate_assignment=True,
):
    """Artifact_Type Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    data_type: str | None = Field(
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
    description: str | None = Field(
        None,
        allow_mutation=False,
        description='The **description** for the Artifact_Type.',
        read_only=True,
        title='description',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    intel_type: str | None = Field(
        None,
        allow_mutation=False,
        description='The **intel type** for the Artifact_Type.',
        read_only=True,
        title='intelType',
    )
    name: str | None = Field(
        None,
        allow_mutation=False,
        description='The **name** for the Artifact_Type.',
        read_only=True,
        title='name',
    )


class ArtifactTypeDataModel(
    BaseModel,
    title='ArtifactType Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Artifact_Types Data Model"""

    data: list[ArtifactTypeModel] | None = Field(
        [],
        description='The data for the ArtifactTypes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class ArtifactTypesModel(
    BaseModel,
    title='ArtifactTypes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Artifact_Types Model"""

    _mode_support = PrivateAttr(False)

    data: list[ArtifactTypeModel] | None = Field(
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


# add forward references
ArtifactTypeDataModel.update_forward_refs()
ArtifactTypeModel.update_forward_refs()
ArtifactTypesModel.update_forward_refs()
