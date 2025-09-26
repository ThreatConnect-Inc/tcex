"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_validator


class PlaybookModel(BaseModel):
    """Playbook Model

    Supported for the following runtimeLevel:
    * Playbook
    """

    tc_playbook_kvstore_context: str | None = Field(
        default=None,
        description='The KV Store context for the current App execution.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_playbook_out_variables: list | None = Field(
        default=None,
        description='The list of requested output variables.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )

    @field_validator('tc_playbook_out_variables', mode='before')
    @classmethod
    def parse_tc_playbook_out_variables(cls, v):
        """Ensure value is an array."""
        if isinstance(v, str):
            v = v.split(',')
        return v
