"""TcEx Framework Module"""

from pydantic import BaseModel, Field


class LoggingModel(BaseModel):
    """Logging Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    # target 50Mb in total log size (1x10Mb + 25x~1.6Mb = ~50Mb)
    tc_log_backup_count: int = Field(
        default=25,
        description='The maximum number of log files to retain for an App.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    tc_log_file: str = Field(
        default='app.log',
        description="The default name of the App's log file.",
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    # job Apps have to collect tc_log_level manually
    tc_log_level: str = Field(
        default='info',
        description='The logging level for the App.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
        # requires_definition=True, # this is true for only Organization runtimeLevel
    )
    tc_log_max_bytes: int = Field(
        default=10_485_760,
        description='The maximum size of the App log file before rotation.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )
    tc_log_to_api: bool = Field(
        default=False,
        description='Flag to enable API logging for the App.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
