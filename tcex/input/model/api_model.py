"""TcEx Framework Module"""

# pylint: disable=no-self-argument

# third-party
from pydantic import BaseModel, Field, validator

# first-party
from tcex.app.config.install_json import InstallJson
from tcex.input.field_type.sensitive import Sensitive


class ApiModel(BaseModel):
    """API Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * TriggerService
    * WebhookTriggerService
    """

    api_default_org: str | None = Field(
        None,
        description='The default ThreatConnect Org for the current API user.',
        inclusion_reason='runtimeLevel',
    )
    # alternate authentication credential when tc_token is not passed
    tc_api_access_id: str | None = Field(
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
    tc_api_secret_key: Sensitive | None = Field(
        None,
        description='A ThreatConnect API Secret Key.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_log_curl: bool = Field(
        False,
        description='Flag to enable logging curl commands.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_token: Sensitive | None = Field(
        None,
        description='A ThreatConnect API token.',
        inclusion_reason='runtimeLevel',
    )
    tc_token_expires: int | None = Field(
        None,
        description='The expiration timestamp in epoch for tc_token.',
        inclusion_reason='runtimeLevel',
    )
    tc_verify: bool = Field(
        True,
        description='Flag to enable SSL validation for API requests.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )

    @validator('tc_token', always=True, pre=True)
    def one_set_of_credentials(cls, v, values):
        """Validate that one set of credentials is provided for the TC API."""
        _ij = InstallJson()

        # external Apps: require credentials and would not have an install.json file
        # organization (job) Apps: require credentials
        # playbook Apps: require credentials
        # service Apps: get token on createConfig message or during request
        if _ij.fqfn.is_file() is False or (
            _ij.model.is_playbook_app or _ij.model.is_organization_app
        ):
            if v is None and not all(
                [values.get('tc_api_access_id'), values.get('tc_api_secret_key')]
            ):
                raise ValueError(
                    'At least one set of ThreatConnect credentials must be provided '
                    '(tc_api_access_id/tc_api_secret key OR tc_token/tc_token_expires).'
                )
        return v
