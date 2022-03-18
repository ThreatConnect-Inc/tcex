"""Indicator Entity Field (Model) Type"""
# standard library
from typing import TYPE_CHECKING, List

# third-party
from pydantic import validator

# first-party
from tcex.input.field_types.exception import InvalidEmptyValue, InvalidEntityType
from tcex.input.field_types.tc_entity import TCEntity

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField

CASE_MANAGEMENT_TYPES = [
    'artifact',
    'case',
    'task',
    'artifact type',
    'notes',
    'workflow event',
    'workflow template',
]


# pylint: disable=no-self-argument, no-self-use
class CaseManagementEntity(TCEntity):
    """Case Management Entity Field (Model) Type"""

    @validator('type')
    def is_empty(cls, value: str, field: 'ModelField') -> str:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    @validator('type')
    def is_type(cls, value: str, field: 'ModelField') -> str:
        """Validate that the entity is of Indicator type."""
        if value.lower() not in CASE_MANAGEMENT_TYPES:
            raise InvalidEntityType(
                field_name=field.name, entity_type='CaseManagement', value=value
            )
        return value


def case_management_entity(case_management_types: List[str] = None) -> type:
    """Return custom model for Case Management Entity."""

    class CustomCaseManagementEntity(CaseManagementEntity):
        """Indicator Entity Field (Model) Type"""

        @validator('type', allow_reuse=True)
        def is_empty(cls, value: str, field: 'ModelField') -> str:
            """Validate that the value is a non-empty string."""
            if isinstance(value, str) and value.replace(' ', '') == '':
                raise InvalidEmptyValue(field_name=field.name)
            return value

        @validator('type', allow_reuse=True)
        def is_type(cls, value: str, field: 'ModelField') -> str:
            """Validate that the entity is of a specific Indicator type."""
            if value.lower() not in [i.lower() for i in case_management_types]:
                raise InvalidEntityType(
                    field_name=field.name, entity_type=str(case_management_types), value=value
                )
            return value

    return CustomCaseManagementEntity


ArtifactEntity: CaseManagementEntity = case_management_entity(case_management_types=['Artifact'])
CaseEntity: CaseManagementEntity = case_management_entity(case_management_types=['Case'])
TaskEntity: CaseManagementEntity = case_management_entity(case_management_types=['Task'])
ArtifactTypeEntity: CaseManagementEntity = case_management_entity(
    case_management_types=['Artifact Type']
)
NoteEntity: CaseManagementEntity = case_management_entity(case_management_types=['Note'])
WorkflowEventEntity: CaseManagementEntity = case_management_entity(
    case_management_types=['Workflow Event']
)
WorkflowTemplateEntity: CaseManagementEntity = case_management_entity(
    case_management_types=['Workflow Template']
)
