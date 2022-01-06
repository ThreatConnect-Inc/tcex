"""Indicator Entity Field (Model) Type"""
# standard library
from typing import TYPE_CHECKING, Dict

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
class IndicatorEntity(TCEntity):
    """Indicator Entity Field (Model) Type"""

    @validator('type')
    def is_empty(cls, value: Dict[str, str], field: 'ModelField') -> Dict[str, str]:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    @validator('type')
    def is_type(cls, value: Dict[str, str], field: 'ModelField') -> Dict[str, str]:
        """Validate that the value is a non-empty string.

        Without the always and pre args, None values will validated before this validator is called.
        """
        ti_utils = ThreatIntelUtils(session_tc=registry.session_tc)
        if value not in ti_utils.indicator_types:
            raise InvalidEntityType(field_name=field.name, entity_type='Indicator', value=value)
        return value
