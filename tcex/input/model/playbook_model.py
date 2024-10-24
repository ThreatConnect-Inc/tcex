"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field, validator


class PlaybookModel(BaseModel):
    """Playbook Model

    Supported for the following runtimeLevel:
    * Playbook
    """

    tc_playbook_kvstore_context: str = Field(
        None,
        description='The KV Store context for the current App execution.',
        inclusion_reason='runtimeLevel',
    )
    tc_playbook_out_variables: list | None = Field(
        None,
        description='The list of requested output variables.',
        inclusion_reason='runtimeLevel',
    )

    @validator('tc_playbook_out_variables', pre=True)
    def parse_tc_playbook_out_variables(cls, v):  # pylint: disable=no-self-argument
        """Ensure value is an array."""
        if isinstance(v, str):
            v = v.split(',')
        return v
