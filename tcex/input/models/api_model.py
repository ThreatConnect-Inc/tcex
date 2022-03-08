"""API Model"""
# pylint: disable=no-self-argument,no-self-use
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Field, validator

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.input.field_types.sensitive import Sensitive


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
    tc_api_secret_key: Optional[Sensitive] = Field(
        None,
        description='A ThreatConnect API Secret Key.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_token: Optional[Sensitive] = Field(
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

    @validator('tc_token', always=True, pre=True)
    def one_set_of_credentials(cls, v, values):  # pylint: disable=E0213,R0201
        """Validate that one set of credentials is provided for the TC API."""
        _ij = InstallJson()

        # external Apps: require credentials and would not have an install.json file
        # organization (job) Apps: require credentials
        # playbook Apps: require credentials
        # service Apps: get token on createConfig message or during request
        if _ij.fqfn.is_file() is False or _ij.model.runtime_level.lower() in [
            'organization',
            'playbook',
        ]:
            if v is None and not all(
                [values.get('tc_api_access_id'), values.get('tc_api_secret_key')]
            ):
                raise ValueError(
                    'At least one set of ThreatConnect credentials must be provided '
                    '(tc_api_access_id/tc_api_secret key OR tc_token/tc_token_expires).'
                )
        return v
