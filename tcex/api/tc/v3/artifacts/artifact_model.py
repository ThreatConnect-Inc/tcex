"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ArtifactModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Artifact Model',
    validate_assignment=True,
):
    """Artifact Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    analytics_priority: str | None = Field(
        None,
        allow_mutation=False,
        description='The **analytics priority** for the Artifact.',
        read_only=True,
        title='analyticsPriority',
    )
    analytics_priority_level: int | None = Field(
        None,
        allow_mutation=False,
        description='The **analytics priority level** for the Artifact.',
        read_only=True,
        title='analyticsPriorityLevel',
    )
    analytics_score: int | None = Field(
        None,
        allow_mutation=False,
        description='The **analytics score** for the Artifact.',
        read_only=True,
        title='analyticsScore',
    )
    analytics_status: str | None = Field(
        None,
        allow_mutation=False,
        description='The **analytics status** for the Artifact.',
        read_only=True,
        title='analyticsStatus',
    )
    analytics_type: str | None = Field(
        None,
        allow_mutation=False,
        description='The **analytics type** for the Artifact.',
        read_only=True,
        title='analyticsType',
    )
    artifact_type: 'ArtifactTypeModel' = Field(
        None,
        allow_mutation=False,
        description='The **artifact type** for the Artifact.',
        read_only=True,
        title='artifactType',
    )
    associated_groups: 'GroupsModel' = Field(
        None,
        description='A list of Groups associated with this Artifact.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    associated_indicators: 'IndicatorsModel' = Field(
        None,
        description='A list of Indicators associated with this Artifact.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedIndicators',
    )
    case_id: int | None = Field(
        None,
        description='The **case id** for the Artifact.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseXid',
        title='caseId',
    )
    case_xid: str | None = Field(
        None,
        description='The **case xid** for the Artifact.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseId',
        title='caseXid',
    )
    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The **date added** for the Artifact.',
        read_only=True,
        title='dateAdded',
    )
    derived_link: bool = Field(
        None,
        description=(
            'Flag to specify if this artifact should be used for potentially associated cases or '
            'not.'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='derivedLink',
    )
    field_name: str | None = Field(
        None,
        description='The field name for the artifact.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fieldName',
    )
    file_data: str | None = Field(
        None,
        description='Base64 encoded file attachment required only for certain artifact types.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileData',
    )
    hash_code: str | None = Field(
        None,
        description='Hashcode of Artifact of type File.',
        methods=['POST'],
        read_only=False,
        title='hashCode',
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
        description='The **intel type** for the Artifact.',
        read_only=True,
        title='intelType',
    )
    links: dict | None = Field(
        None,
        allow_mutation=False,
        description='The **links** for the Artifact.',
        read_only=True,
        title='links',
    )
    notes: 'NotesModel' = Field(
        None,
        description='A list of Notes corresponding to the Artifact.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='notes',
    )
    parent_case: 'CaseModel' = Field(
        None,
        allow_mutation=False,
        description='The **parent case** for the Artifact.',
        read_only=True,
        title='parentCase',
    )
    source: str | None = Field(
        None,
        description='The **source** for the Artifact.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='source',
    )
    summary: str | None = Field(
        None,
        description='The **summary** for the Artifact.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='summary',
    )
    task: 'TaskModel' = Field(
        None,
        allow_mutation=False,
        description='The **task** for the Artifact.',
        read_only=True,
        title='task',
    )
    task_id: int | None = Field(
        None,
        description='The ID of the task which the Artifact references.',
        methods=['POST'],
        read_only=False,
        title='taskId',
    )
    task_xid: str | None = Field(
        None,
        description='The XID of the task which the Artifact references.',
        methods=['POST'],
        read_only=False,
        title='taskXid',
    )
    type: str | None = Field(
        None,
        description='The **type** for the Artifact.',
        methods=['POST'],
        read_only=False,
        title='type',
    )

    @validator('artifact_type', always=True, pre=True)
    def _validate_artifact_type(cls, v):
        if not v:
            return ArtifactTypeModel()  # type: ignore
        return v

    @validator('parent_case', always=True, pre=True)
    def _validate_case(cls, v):
        if not v:
            return CaseModel()  # type: ignore
        return v

    @validator('associated_groups', always=True, pre=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @validator('associated_indicators', always=True, pre=True)
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()  # type: ignore
        return v

    @validator('notes', always=True, pre=True)
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()  # type: ignore
        return v

    @validator('task', always=True, pre=True)
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
        methods=['POST', 'PUT'],
        title='data',
    )


class ArtifactsModel(
    BaseModel,
    title='Artifacts Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Artifacts Model"""

    _mode_support = PrivateAttr(True)

    data: list[ArtifactModel] | None = Field(
        [],
        description='The data for the Artifacts.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


# first-party
from tcex.api.tc.v3.artifact_types.artifact_type_model import ArtifactTypeModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.notes.note_model import NotesModel
from tcex.api.tc.v3.tasks.task_model import TaskModel

# add forward references
ArtifactDataModel.update_forward_refs()
ArtifactModel.update_forward_refs()
ArtifactsModel.update_forward_refs()
