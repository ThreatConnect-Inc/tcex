"""Indicator Entity Field (Model) Type"""
# standard library
from typing import TYPE_CHECKING, List

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
    def is_empty(cls, value: str, field: 'ModelField') -> str:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    @validator('type')
    def is_type(cls, value: str, field: 'ModelField') -> str:
        """Validate that the entity is of Indicator type."""
        ti_utils = ThreatIntelUtils(session_tc=registry.session_tc)
        if value not in ti_utils.indicator_types:
            raise InvalidEntityType(field_name=field.name, entity_type='Indicator', value=value)
        return value


def indicator_entity(indicator_types: List[str] = None) -> type:
    """Return custom model for Indicator Entity."""

    class CustomIndicatorEntity(IndicatorEntity):
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
            if value.lower() not in [i.lower() for i in indicator_types]:
                raise InvalidEntityType(
                    field_name=field.name, entity_type=str(indicator_types), value=value
                )
            return value

    return CustomIndicatorEntity


AddressEntity: IndicatorEntity = indicator_entity(indicator_types=['Address'])
EmailAddressEntity: IndicatorEntity = indicator_entity(indicator_types=['EmailAddress'])
HostEntity: IndicatorEntity = indicator_entity(indicator_types=['Host'])
FileEntity: IndicatorEntity = indicator_entity(indicator_types=['File'])
UrlEntity: IndicatorEntity = indicator_entity(indicator_types=['URL'])
