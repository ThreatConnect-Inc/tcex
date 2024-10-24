"""TcEx Framework Module"""

# standard library
import tempfile
from pathlib import Path

# third-party
from pydantic import BaseModel, Field


class PathModel(BaseModel):
    """Path Model

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

    tc_in_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "in" directory.',
        inclusion_reason='runtimeLevel',
    )
    tc_log_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "log" directory.',
        inclusion_reason='runtimeLevel',
    )
    tc_out_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "out" directory.',
        inclusion_reason='runtimeLevel',
    )
    tc_temp_path: Path = Field(
        Path(tempfile.gettempdir()),
        description='The path to the Apps "tmp" directory.',
        inclusion_reason='runtimeLevel',
    )
