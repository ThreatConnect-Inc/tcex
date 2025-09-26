"""TcEx Framework Module"""

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic_core.core_schema import ValidationInfo

from tcex.input.field_type.exception import InvalidEmptyValue


class TCEntity(BaseModel):
    """Model for TCEntity Input."""

    id: int
    type: str
    value: str

    # IMPORTANT: confidence and rating values are included only so that, when defined,
    #    they come back as the correct types. They are only intended for Indicator
    #    types and are not guaranteed to be populated.
    confidence: int | None = None
    rating: int | None = None

    @field_validator('id', 'type', 'value')
    @classmethod
    def non_empty_string(cls, v: dict[str, str], info: ValidationInfo) -> dict[str, str]:
        """Validate that the value is a non-empty string."""
        if isinstance(v, str) and v.replace(' ', '') == '':  # None value are automatically covered
            raise InvalidEmptyValue(field_name=info.field_name or 'Unknown')
        return v

    model_config = ConfigDict(extra='allow', validate_assignment=True)
