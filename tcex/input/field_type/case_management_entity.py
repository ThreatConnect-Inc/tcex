"""TcEx Framework Module"""

# standard library
from typing import ClassVar

# third-party
from pydantic import create_model, validator
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_type.exception import InvalidEmptyValue, InvalidEntityType
from tcex.input.field_type.tc_entity import TCEntity

CASE_MANAGEMENT_TYPES = [
    'artifact',
    'case',
    'task',
    'artifact type',
    'notes',
    'workflow event',
    'workflow template',
]


# pylint: disable=no-self-argument
class CaseManagementEntity(TCEntity):
    """Case Management Entity Field (Model) Type"""

    case_management_types: ClassVar[list[str]] = CASE_MANAGEMENT_TYPES

    @validator('type', allow_reuse=True)
    def is_empty(cls, value: str, field: ModelField) -> str:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    @validator('type', allow_reuse=True)
    def is_type(cls, value: str, field: ModelField) -> str:
        """Validate that the entity is of Indicator type."""
        if value.lower() not in [i.lower() for i in cls.case_management_types]:
            raise InvalidEntityType(
                field_name=field.name, entity_type=str(cls.case_management_types), value=value
            )
        return value


def case_management_entity(
    case_management_types: list[str], model_name: str = 'CustomCaseManagementEntity'
) -> type[CaseManagementEntity]:
    """Dynamically create a Case Management Entity model."""
    return create_model(
        model_name,
        case_management_types=(ClassVar[list[str]], case_management_types),
        __base__=CaseManagementEntity,
    )


ArtifactEntity = case_management_entity(case_management_types=['Artifact'])
CaseEntity = case_management_entity(case_management_types=['Case'])
TaskEntity = case_management_entity(case_management_types=['Task'])
ArtifactTypeEntity = case_management_entity(case_management_types=['Artifact Type'])
NoteEntity = case_management_entity(case_management_types=['Note'])
WorkflowEventEntity = case_management_entity(case_management_types=['Workflow Event'])
WorkflowTemplateEntity = case_management_entity(case_management_types=['Workflow Template'])
