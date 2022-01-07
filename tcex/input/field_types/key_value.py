"""KeyValue Playbook Type"""
# standard library
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

# third-party
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_types.binary import Binary
from tcex.input.field_types.exception import InvalidEmptyValue
from tcex.input.field_types.string import String
from tcex.input.field_types.tc_entity import TCEntity

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


# pylint: disable=no-self-argument, no-self-use
class KeyValue(BaseModel):
    """Model for KeyValue Input."""

    key: str
    type: Optional[str]
    value: Union[
        List['KeyValue'],
        'KeyValue',
        List[TCEntity],
        TCEntity,
        List[String],
        String,
        List[Binary],
        Binary,
    ]

    @validator('key')
    def non_empty_string(cls, value: str, field: 'ModelField') -> Dict[str, Any]:
        """Validate that the value is a non-empty string."""
        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    class Config:
        """Model Config"""

        validate_assignment = True


KeyValue.update_forward_refs()
