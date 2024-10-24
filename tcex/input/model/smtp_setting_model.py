"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field

# first-party
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
        None,
        description='The SMTP server hostname.',
        inclusion_reason='feature (smtpSettings)',
    )
    tc_smtp_password: Sensitive = Field(
        None,
        description='The SMTP server password.',
        inclusion_reason='feature (smtpSettings)',
    )
    tc_smtp_port: int = Field(
        None,
        description='The SMTP server port number.',
        inclusion_reason='feature (smtpSettings)',
    )
    tc_smtp_username: str = Field(
        None,
        description='The SMTP server username.',
        inclusion_reason='feature (smtpSettings)',
    )
    tc_sys_email: str = Field(
        None,
        description='The system level email address.',
        inclusion_reason='feature (smtpSettings)',
    )
