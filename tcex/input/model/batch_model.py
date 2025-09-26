"""TcEx Framework Module"""

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
        default='Create',
        description='The action for the Batch Job.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    batch_chunk: int = Field(
        default=25_000,
        description='The maximum number of item to send in batch request.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    batch_halt_on_error: bool = Field(
        default=False,
        description='Flag to control batch job failure behavior.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    batch_poll_interval: int = Field(
        default=15,
        description='The poll interval in second for the batch job.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    batch_poll_interval_max: int = Field(
        default=3_600,
        description='The maximum poll interval in seconds for the batch job.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    batch_write_type: str = Field(
        default='Append',
        description='The API setting for batch to control write behavior.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
