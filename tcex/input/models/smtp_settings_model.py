"""SMTP Settings Model"""
# third-party
from pydantic import BaseModel


class SmtpSettingsModel(BaseModel):
    """SMTP Settings Model

    Feature: smtpSettings

    Supported for the following runtimeLevel:
    * ApiService
    * Organization
    * Playbook
    * WebhookTriggerService
    * TriggerService
    """

    # the smtp host
    tc_smtp_host: str

    # the smtp password
    tc_smtp_password: str

    # the smtp port
    tc_smtp_port: int

    # the smtp username
    tc_smtp_username: str

    # the system level email
    tc_sys_email: str
