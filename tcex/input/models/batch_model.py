"""Batch Model"""
# third-party
from pydantic import BaseModel


class BatchModel(BaseModel):
    """Batch Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * WebhookTriggerService
    * TriggerService
    """

    #
    # TcEx Specific
    #

    # the batch action
    batch_action: str = 'Create'

    # the chunk size for batch submissions
    batch_chunk: int = 25_000

    # the API setting for batch to control failure behavior
    batch_halt_on_error: bool = False

    # the poll interval in seconds for the TcEx batch module
    batch_poll_interval: int = 15

    # the maximum poll interval in seconds for the TcEx batch module
    batch_poll_interval_max: int = 3_600

    # the API setting for batch to control write behavior
    batch_write_type: str = 'Append'
