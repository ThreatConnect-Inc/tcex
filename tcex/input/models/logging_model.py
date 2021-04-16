"""Logging Model"""
# third-party
from pydantic import BaseModel


class LoggingModel(BaseModel):
    """Logging Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    #
    # ThreatConnect Provided Inputs
    #

    # the logging level for the App (job Apps have to collect this manually)
    tc_log_level: str = 'info'

    # if True, enable logging to ThreatConnect API
    # exceptions: [ApiService, WebhookTriggerService, TriggerService]
    tc_log_to_api: bool = False

    #
    # TcEx Specific
    #

    # the maximum number of log files to retain
    tc_log_backup_count: int = 25  # target 50Mb in total log size (1x10Mb + 25x~1.6Mb = ~50Mb)

    # if True, log message showing how to make API calls with curl are enabled
    tc_log_curl: bool = False

    # the name of the App log file
    tc_log_file: str = 'app.log'

    # the maximum size of the App log file before rotation
    tc_log_max_bytes: int = 10_485_760  # 10Mb
