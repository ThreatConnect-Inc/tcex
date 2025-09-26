"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ArtifactModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Artifact Model',
    validate_assignment=True,
):
    """Artifact Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=True)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    analytics_priority: str | None = Field(
        default=None,
        description='The **analytics priority** for the Artifact.',
        frozen=True,
        title='analyticsPriority',
        validate_default=True,
    )
    analytics_priority_level: int | None = Field(
        default=None,
        description='The **analytics priority level** for the Artifact.',
        frozen=True,
        title='analyticsPriorityLevel',
        validate_default=True,
    )
    analytics_score: int | None = Field(
        default=None,
        description='The **analytics score** for the Artifact.',
        frozen=True,
        title='analyticsScore',
        validate_default=True,
    )
    analytics_status: str | None = Field(
        default=None,
        description='The **analytics status** for the Artifact.',
        frozen=True,
        title='analyticsStatus',
        validate_default=True,
    )
    analytics_type: str | None = Field(
        default=None,
        description='The **analytics type** for the Artifact.',
        frozen=True,
        title='analyticsType',
        validate_default=True,
    )
    artifact_type: ArtifactTypeModel | None = Field(
        default=None,
        description='The **artifact type** for the Artifact.',
        frozen=True,
        title='artifactType',
        validate_default=True,
    )
    associated_groups: GroupsModel | None = Field(
        default=None,
        description='A list of Groups associated with this Artifact.',
        title='associatedGroups',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_indicators: IndicatorsModel | None = Field(
        default=None,
        description='A list of Indicators associated with this Artifact.',
        title='associatedIndicators',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    case_id: int | None = Field(
        default=None,
        description='The **case id** for the Artifact.',
        title='caseId',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseXid'},
    )
    case_xid: str | None = Field(
        default=None,
        description='The **case xid** for the Artifact.',
        title='caseXid',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseId'},
    )
    date_added: datetime | None = Field(
        default=None,
        description='The **date added** for the Artifact.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    derived_link: bool | None = Field(
        default=None,
        description=(
            'Flag to specify if this artifact should be used for potentially associated cases or '
            'not.'
        ),
        title='derivedLink',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    field_name: str | None = Field(
        default=None,
        description='The field name for the artifact.',
        title='fieldName',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    file_data: str | None = Field(
        default=None,
        description='Base64 encoded file attachment required only for certain artifact types.',
        title='fileData',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    hash_code: str | None = Field(
        default=None,
        description='Hashcode of Artifact of type File.',
        title='hashCode',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    intel_type: str | None = Field(
        default=None,
        description='The **intel type** for the Artifact.',
        frozen=True,
        title='intelType',
        validate_default=True,
    )
    links: dict | None = Field(
        default=None,
        description='The **links** for the Artifact.',
        frozen=True,
        title='links',
        validate_default=True,
    )
    notes: NotesModel | None = Field(
        default=None,
        description='A list of Notes corresponding to the Artifact.',
        title='notes',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    parent_case: CaseModel | None = Field(
        default=None,
        description='The **parent case** for the Artifact.',
        frozen=True,
        title='parentCase',
        validate_default=True,
    )
    source: str | None = Field(
        default=None,
        description='The **source** for the Artifact.',
        title='source',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    summary: str | None = Field(
        default=None,
        description='The **summary** for the Artifact.',
        title='summary',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    task: TaskModel | None = Field(
        default=None,
        description='The **task** for the Artifact.',
        frozen=True,
        title='task',
        validate_default=True,
    )
    task_id: int | None = Field(
        default=None,
        description='The ID of the task which the Artifact references.',
        title='taskId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    task_xid: str | None = Field(
        default=None,
        description='The XID of the task which the Artifact references.',
        title='taskXid',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    type: str | None = Field(
        default=None,
        description='The **type** for the Artifact.',
        title='type',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )

    @field_validator('artifact_type', mode='before')
    @classmethod
    def _validate_artifact_type(cls, v):
        if not v:
            return ArtifactTypeModel()  # type: ignore
        return v

    @field_validator('parent_case', mode='before')
    @classmethod
    def _validate_case(cls, v):
        if not v:
            return CaseModel()  # type: ignore
        return v

    @field_validator('associated_groups', mode='before')
    @classmethod
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @field_validator('associated_indicators', mode='before')
    @classmethod
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()  # type: ignore
        return v

    @field_validator('notes', mode='before')
    @classmethod
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()  # type: ignore
        return v

    @field_validator('task', mode='before')
    @classmethod
    def _validate_task(cls, v):
        if not v:
            return TaskModel()  # type: ignore
        return v


class ArtifactDataModel(
    BaseModel,
    title='Artifact Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Artifacts Data Model"""

    data: list[ArtifactModel] | None = Field(
        [],
        description='The data for the Artifacts.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class ArtifactsModel(
    BaseModel,
    title='Artifacts Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Artifacts Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list[ArtifactModel] | None = Field(
        [],
        description='The data for the Artifacts.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.artifact_types.artifact_type_model import ArtifactTypeModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.notes.note_model import NotesModel
from tcex.api.tc.v3.tasks.task_model import TaskModel

# rebuild model
ArtifactDataModel.model_rebuild()
ArtifactModel.model_rebuild()
ArtifactsModel.model_rebuild()
