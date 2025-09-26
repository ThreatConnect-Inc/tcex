"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ArtifactTypeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='ArtifactType Model',
    validate_assignment=True,
):
    """Artifact_Type Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=True)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    data_type: str | None = Field(
        default=None,
        description='The **data type** for the Artifact_Type.',
        frozen=True,
        title='dataType',
        validate_default=True,
    )
    derived_link: bool | None = Field(
        default=None,
        description='The **derived link** for the Artifact_Type.',
        frozen=True,
        title='derivedLink',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='The **description** for the Artifact_Type.',
        frozen=True,
        title='description',
        validate_default=True,
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    intel_type: str | None = Field(
        default=None,
        description='The **intel type** for the Artifact_Type.',
        frozen=True,
        title='intelType',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The **name** for the Artifact_Type.',
        frozen=True,
        title='name',
        validate_default=True,
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
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class ArtifactTypesModel(
    BaseModel,
    title='ArtifactTypes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Artifact_Types Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[ArtifactTypeModel] | None = Field(
        [],
        description='The data for the ArtifactTypes.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
ArtifactTypeDataModel.model_rebuild()
ArtifactTypeModel.model_rebuild()
ArtifactTypesModel.model_rebuild()
