"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field


class BatchModel(BaseModel):
    """Batch Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    #
    # TcEx Specific
    #

    batch_action: str = Field(
        'Create',
        description='The action for the Batch Job.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    batch_chunk: int = Field(
        25_000,
        description='The maximum number of item to send in batch request.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    batch_halt_on_error: bool = Field(
        False,
        description='Flag to control batch job failure behavior.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    batch_poll_interval: int = Field(
        15,
        description='The poll interval in second for the batch job.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    batch_poll_interval_max: int = Field(
        3_600,
        description='The maximum poll interval in seconds for the batch job.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    batch_write_type: str = Field(
        'Append',
        description='The API setting for batch to control write behavior.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
