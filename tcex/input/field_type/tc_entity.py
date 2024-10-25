"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Extra, validator
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_type.exception import InvalidEmptyValue


# pylint: disable=no-self-argument
class TCEntity(BaseModel):
    """Model for TCEntity Input."""

    id: int
    type: str
    value: str

    # IMPORTANT: confidence and rating values are included only so that, when defined,
    #    they come back as the correct types. They are only intended for Indicator
    #    types and are not guaranteed to be populated.
    confidence: int | None
    rating: int | None

    @validator('id', 'type', 'value')
    def non_empty_string(cls, v: dict[str, str], field: ModelField) -> dict[str, str]:
        """Validate that the value is a non-empty string."""
        if isinstance(v, str) and v.replace(' ', '') == '':  # None value are automatically covered
            raise InvalidEmptyValue(field_name=field.name)
        return v

    class Config:
        """Model Config"""

        extra = Extra.allow
        validate_assignment = True
