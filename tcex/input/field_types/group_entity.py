"""Group Entity Field (Model) Type"""
# standard library
from typing import TYPE_CHECKING, Dict, List

# third-party
from pydantic import validator

# first-party
from tcex.api.tc.utils.threat_intel_utils import ThreatIntelUtils
from tcex.input.field_types.exception import InvalidEmptyValue, InvalidEntityType
from tcex.input.field_types.tc_entity import TCEntity
from tcex.pleb.registry import registry

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


# pylint: disable=no-self-argument, no-self-use
class GroupEntity(TCEntity):
    """Group Entity Field (Model) Type"""

    @validator('type')
    def is_type(cls, value: str, field: 'ModelField') -> str:
        """Validate that the value is a non-empty string.

        Without the always and pre args, None values will validated before this validator is called.
        """
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)

        ti_utils = ThreatIntelUtils(session_tc=registry.session_tc)
        if value not in ti_utils.group_types:
            raise InvalidEntityType(field_name=field.name, entity_type='Group', value=value)
        return value


def group_entity(group_types: List[str] = None) -> type:
    """Return custom model for Group Entity."""

    class CustomGroupEntity(GroupEntity):
        """Group Entity Field (Model) Type"""

        @validator('type', allow_reuse=True)
        def is_empty(cls, value: str, field: 'ModelField') -> Dict[str, str]:
            """Validate that the value is a non-empty string."""
            if isinstance(value, str) and value.replace(' ', '') == '':
                raise InvalidEmptyValue(field_name=field.name)
            return value

        @validator('type', allow_reuse=True)
        def is_type(cls, value: str, field: 'ModelField') -> Dict[str, str]:
            """Validate that the entity is of a specific Group type."""
            if value.lower() not in [i.lower() for i in group_types]:
                raise InvalidEntityType(
                    field_name=field.name, entity_type=str(group_types), value=value
                )
            return value

    return CustomGroupEntity


AdversaryEntity: GroupEntity = group_entity(group_types=['Adversary'])
CampaignEntity: GroupEntity = group_entity(group_types=['Campaign'])
DocumentEntity: GroupEntity = group_entity(group_types=['Document'])
EmailEntity: GroupEntity = group_entity(group_types=['Email'])
EventEntity: GroupEntity = group_entity(group_types=['Event'])
IncidentEntity: GroupEntity = group_entity(group_types=['Incident'])
IntrusionSetEntity: GroupEntity = group_entity(group_types=['Intrusion Set'])
SignatureEntity: GroupEntity = group_entity(group_types=['Signature'])
ReportEntity: GroupEntity = group_entity(group_types=['Report'])
ThreatEntity: GroupEntity = group_entity(group_types=['Threat'])
TaskEntity: GroupEntity = group_entity(group_types=['Task'])
