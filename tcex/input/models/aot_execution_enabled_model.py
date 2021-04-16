"""AOT Execution Enabled Model"""
# third-party
from pydantic import BaseModel


class AotExecutionEnabledModel(BaseModel):
    """AOT Execution Enabled Model

    Feature: aotExecutionEnabled

    Supported for the following runtimeLevel:
    * Playbook
    """

    # the AOT channel to monitor for action [pb]
    tc_action_channel: str

    # if True, AOT execution is enabled [pb]
    tc_aot_enabled: bool = False

    # the AOT channel to send exit messages [pb]
    tc_exit_channel: str

    # the number of seconds to wait for action message [pb]
    tc_terminate_seconds: int
