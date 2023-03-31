"""TcEx Framework Module"""
# third-party
from pydantic import BaseModel, Field


class AotExecutionEnabledModel(BaseModel):
    """AOT Execution Enabled Model

    Feature: aotExecutionEnabled

    Supported for the following runtimeLevel:
    * Playbook
    """

    tc_action_channel: str = Field(
        None,
        description='The AOT channel to monitor for incoming action.',
        inclusion_reason='feature (aotExecutionEnabled)',
    )
    tc_aot_enabled: bool = Field(
        False,
        description='Flag to enable AOT mode for the App.',
        inclusion_reason='feature (aotExecutionEnabled)',
    )
    tc_exit_channel: str = Field(
        None,
        description='The AOT channel to send the exit message.',
        inclusion_reason='feature (aotExecutionEnabled)',
    )
    tc_terminate_seconds: int = Field(
        None,
        description='The max number of second to wait for action message.',
        inclusion_reason='feature (aotExecutionEnabled)',
    )
