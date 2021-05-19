"""API Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Field, SecretStr


class ApiModel(BaseModel):
    """API Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * TriggerService
    * WebhookTriggerService
    """

    api_default_org: Optional[str] = Field(
        None,
        description='The default ThreatConnect Org for the current API user.',
        inclusion_reason='runtimeLevel',
    )
    # alternate authentication credential when tc_token is not passed
    tc_api_access_id: Optional[str] = Field(
        None,
        description='A ThreatConnect API Access Id.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_api_path: str = Field(
        'https://api.threatconnect.com',
        description='The URL for the ThreatConnect API.',
        inclusion_reason='runtimeLevel',
    )
    # alternate authentication credential when tc_token is not passed
    tc_api_secret_key: Optional[SecretStr] = Field(
        None,
        description='A ThreatConnect API Secret Key.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_token: Optional[SecretStr] = Field(
        None,
        description='A ThreatConnect API token.',
        inclusion_reason='runtimeLevel',
    )
    tc_token_expires: Optional[int] = Field(
        None,
        description='The expiration timestamp in epoch for tc_token.',
        inclusion_reason='runtimeLevel',
    )
    tc_verify: Optional[bool] = Field(
        True,
        description='Flag to enable SSL validation for API requests.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
