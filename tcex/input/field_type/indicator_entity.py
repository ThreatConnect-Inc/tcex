"""TcEx Framework Module"""

from typing import ClassVar

from pydantic import create_model, field_validator
from pydantic_core import core_schema

from tcex.api.tc.util.threat_intel_util import ThreatIntelUtil
from tcex.input.field_type.exception import InvalidEmptyValue, InvalidEntityType
from tcex.input.field_type.tc_entity import TCEntity
from tcex.registry import registry


class IndicatorEntity(TCEntity):
    """Indicator Entity Field (Model) Type"""

    indicator_types: ClassVar[list[str]] = []

    @field_validator('type')
    @classmethod
    def is_empty(cls, value: str, info: core_schema.ValidationInfo) -> str:
        """Validate that the value is a non-empty string."""
        field_name = info.field_name or '--unknown--'
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field_name)
        return value

    @field_validator('type')
    @classmethod
    def is_type(cls, value: str, info: core_schema.ValidationInfo) -> str:
        """Validate that the entity is of a specific Indicator type."""
        field_name = info.field_name or '--unknown--'
        ti_utils = ThreatIntelUtil(session_tc=registry.session_tc)
        indicator_types = cls.indicator_types or ti_utils.indicator_types
        if value.lower() not in [i.lower() for i in indicator_types]:
            raise InvalidEntityType(
                field_name=field_name, entity_type=str(indicator_types), value=value
            )
        return value


def indicator_entity(
    indicator_types: list[str], model_name: str = 'CustomIndicatorEntity'
) -> type[IndicatorEntity]:
    """Dynamically create a Case Management Entity model."""
    return create_model(
        model_name,
        indicator_types=(ClassVar[list[str]], indicator_types),
        __base__=IndicatorEntity,
    )


AddressEntity = indicator_entity(indicator_types=['Address'])
EmailAddressEntity = indicator_entity(indicator_types=['EmailAddress'])
HostEntity = indicator_entity(indicator_types=['Host'])
FileEntity = indicator_entity(indicator_types=['File'])
UrlEntity = indicator_entity(indicator_types=['URL'])
