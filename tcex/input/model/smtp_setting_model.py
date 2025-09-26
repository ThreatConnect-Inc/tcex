"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_serializer

from tcex.input.field_type.sensitive import Sensitive


class SmtpSettingModel(BaseModel):
    """SMTP Setting Model

    Feature: smtpSettings

    Supported for the following runtimeLevel:
    * ApiService
    * Organization
    * Playbook
    * WebhookTriggerService
    * TriggerService
    """

    tc_smtp_host: str = Field(
        default=...,
        description='The SMTP server hostname.',
        json_schema_extra={'inclusion_reason': 'feature (smtpSettings)'},
    )
    tc_smtp_password: Sensitive = Field(
        default=...,
        description='The SMTP server password.',
        json_schema_extra={'inclusion_reason': 'feature (smtpSettings)'},
    )
    tc_smtp_port: int = Field(
        default=...,
        description='The SMTP server port number.',
        json_schema_extra={'inclusion_reason': 'feature (smtpSettings)'},
    )
    tc_smtp_username: str = Field(
        default=...,
        description='The SMTP server username.',
        json_schema_extra={'inclusion_reason': 'feature (smtpSettings)'},
    )
    tc_sys_email: str = Field(
        default=...,
        description='The system level email address.',
        json_schema_extra={'inclusion_reason': 'feature (smtpSettings)'},
    )

    @field_serializer('tc_smtp_password', when_used='json')
    def convert_sensitive_to_str(self, value: Sensitive | None):
        """."""
        return str(value)
