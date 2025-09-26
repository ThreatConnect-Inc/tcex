"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_serializer

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
        json_schema_extra={'inclusion_reason': 'feature (CALSettings)'},
    )
    tc_cal_token: Sensitive = Field(
        ...,
        description='The token for CAL.',
        json_schema_extra={
            'inclusion_reason': 'feature (CALSettings)',
        },
    )
    tc_cal_timestamp: int = Field(
        ...,
        description='The expiration timestamp in epoch for tc_cal_token.',
        json_schema_extra={
            'inclusion_reason': 'feature (CALSettings)',
        },
    )

    @field_serializer('tc_cal_token', when_used='json')
    def convert_sensitive_to_str(self, value: Sensitive | None):
        """."""
        return str(value)
