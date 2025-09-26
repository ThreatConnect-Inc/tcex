"""TcEx Framework Module"""

from typing import ClassVar

from pydantic import create_model, field_validator
from pydantic_core.core_schema import ValidationInfo

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


class CaseManagementEntity(TCEntity):
    """Case Management Entity Field (Model) Type"""

    case_management_types: ClassVar[list[str]] = CASE_MANAGEMENT_TYPES

    @field_validator('type')
    @classmethod
    def is_empty(cls, value: str, info: ValidationInfo) -> str:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=info.field_name or '--unknown--')
        return value

    @field_validator('type')
    @classmethod
    def is_type(cls, value: str, info: ValidationInfo) -> str:
        """Validate that the entity is of Indicator type."""
        if value.lower() not in [i.lower() for i in cls.case_management_types]:
            raise InvalidEntityType(
                field_name=info.field_name or '--unknown--',
                entity_type=str(cls.case_management_types),
                value=value,
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
