"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field

# first-party
from tcex.input.field_type.sensitive import Sensitive


class CalSettingModel(BaseModel):
    """CAL Settings Model

    Feature: CALSettings

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * WebhookTriggerService
    * TriggerService
    """

    #
    # ThreatConnect Provided Inputs
    #

    tc_cal_host: str = Field(
        ...,
        description='The hostname for CAL.',
        inclusion_reason='feature (CALSettings)',
    )
    tc_cal_token: Sensitive = Field(
        ...,
        description='The token for CAL.',
        inclusion_reason='feature (CALSettings)',
    )
    tc_cal_timestamp: int = Field(
        ...,
        description='The expiration timestamp in epoch for tc_cal_token.',
        inclusion_reason='feature (CALSettings)',
    )
