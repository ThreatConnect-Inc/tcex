"""TCEntity Playbook Type"""
# standard library
from typing import Dict

# third-party
from pydantic import validator

# first-party
from tcex.api.tc.utils.threat_intel_utils import ThreatIntelUtils
from tcex.input.field_models.tc_entity import TCEntity
from tcex.pleb.registry import registry


# pylint: disable=no-self-argument, no-self-use
class GroupEntity(TCEntity):
    """Model for TCEntity Input."""

    @validator('type')
    def is_type(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate that the value is a non-empty string."""
        if isinstance(v, str) and v.replace(' ', '') == '':  # None value are automatically covered
            raise ValueError('Empty value is not allowed.')

        if v == '':  # None value are automatically covered
            raise ValueError('Empty value is not allowed.')

        ti_utils = ThreatIntelUtils(session_tc=registry.session_tc)
        if v not in ti_utils.group_types:
            raise ValueError('The provided Entity is not a Group Entity.')
        return v
