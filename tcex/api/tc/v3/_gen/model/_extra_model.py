"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_validator

from tcex.util.string_operation import CamelString


class ExtraModel(
    BaseModel,
    arbitrary_types_allowed=True,
    extra='forbid',
    title='Extra Model',
    validate_assignment=True,
):
    """Model Definition"""

    alias: CamelString = Field(..., description='Field alias.', validate_default=True)
    import_data: str | None = Field(None, description='The import data.')
    import_source: str | None = Field(
        None, description='The source of the import: standard library, first-party, etc.'
    )
    methods: list[str] = Field([], description='Field methods.')
    model: str | None = Field(None, description='The type model.')
    type: CamelString = Field(..., description='The type of the property.', validate_default=True)
    typing_type: str = Field(..., description='The Python typing hint type.')

    @field_validator('alias', 'type', mode='before')
    @classmethod
    def _camel_string(cls, v):
        """Convert to CamelString."""
        return CamelString(v)
