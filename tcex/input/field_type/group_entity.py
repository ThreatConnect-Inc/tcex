"""TcEx Framework Module"""

# standard library
from typing import ClassVar

# third-party
from pydantic import create_model, validator
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.api.tc.util.threat_intel_util import ThreatIntelUtil
from tcex.input.field_type.exception import InvalidEmptyValue, InvalidEntityType
from tcex.input.field_type.tc_entity import TCEntity
from tcex.registry import registry


# pylint: disable=no-self-argument
class GroupEntity(TCEntity):
    """Group Entity Field (Model) Type"""

    group_types: ClassVar[list[str]] = []

    @validator('type', allow_reuse=True)
    def is_empty(cls, value: str, field: ModelField) -> str:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    @validator('type', allow_reuse=True)
    def is_type(cls, value: str, field: ModelField) -> str:
        """Validate that the value is a non-empty string.

        Without the always and pre args, None values will validated before this validator is called.
        """
        ti_utils = ThreatIntelUtil(session_tc=registry.session_tc)
        group_types = cls.group_types or ti_utils.group_types
        if value.lower() not in [i.lower() for i in group_types]:
            raise InvalidEntityType(
                field_name=field.name, entity_type=str(group_types), value=value
            )
        return value


def group_entity(
    group_types: list[str], model_name: str = 'CustomGroupEntity'
) -> type[GroupEntity]:
    """Dynamically create a Case Management Entity model."""
    return create_model(
        model_name,
        group_types=(ClassVar[list[str]], group_types),
        __base__=GroupEntity,
    )


AdversaryEntity = group_entity(group_types=['Adversary'])
CampaignEntity = group_entity(group_types=['Campaign'])
DocumentEntity = group_entity(group_types=['Document'])
EmailEntity = group_entity(group_types=['Email'])
EventEntity = group_entity(group_types=['Event'])
IncidentEntity = group_entity(group_types=['Incident'])
IntrusionSetEntity = group_entity(group_types=['Intrusion Set'])
SignatureEntity = group_entity(group_types=['Signature'])
ReportEntity = group_entity(group_types=['Report'])
ThreatEntity = group_entity(group_types=['Threat'])
TaskEntity = group_entity(group_types=['Task'])
