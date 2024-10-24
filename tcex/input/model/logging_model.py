"""TcEx Framework Module"""

# third-party
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
        25,
        description='The maximum number of log files to retain for an App.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_log_file: str = Field(
        'app.log',
        description='The default name of the App\'s log file.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    # job Apps have to collect tc_log_level manually
    tc_log_level: str = Field(
        'info',
        description='The logging level for the App.',
        inclusion_reason='runtimeLevel',
        # requires_definition=True, # this is true for only Organization runtimeLevel
    )
    tc_log_max_bytes: int = Field(
        10_485_760,
        description='The maximum size of the App log file before rotation.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_log_to_api: bool = Field(
        False,
        description='Flag to enable API logging for the App.',
        inclusion_reason='runtimeLevel',
    )
