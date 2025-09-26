"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_serializer

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
        default=None,
        description='The default ThreatConnect Org for the current API user.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
        },
    )
    # alternate authentication credential when tc_token is not passed
    tc_api_access_id: str | None = Field(
        default=None,
        description='A ThreatConnect API Access Id.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel', 'requires_definition': True},
    )
    tc_api_path: str = Field(
        'https://api.threatconnect.com',
        description='The URL for the ThreatConnect API.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
        },
    )
    # alternate authentication credential when tc_token is not passed
    tc_api_secret_key: Sensitive | None = Field(
        None,
        description='A ThreatConnect API Secret Key.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel', 'requires_definition': True},
    )
    tc_log_curl: bool = Field(
        default=False,
        description='Flag to enable logging curl commands.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel', 'requires_definition': True},
    )
    tc_token: Sensitive | None = Field(
        None,
        description='A ThreatConnect API token.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
        },
    )
    tc_token_expires: int | None = Field(
        None,
        description='The expiration timestamp in epoch for tc_token.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
        },
    )
    tc_verify: bool = Field(
        default=True,
        description='Flag to enable SSL validation for API requests.',
        json_schema_extra={
            'inclusion_reason': 'runtimeLevel',
            'requires_definition': True,
        },
    )

    @field_serializer('tc_api_secret_key', 'tc_token', when_used='json')
    def convert_sensitive_to_str(self, value: Sensitive | None):
        """."""
        return str(value)

    # TODO: [high] this method corrupts the current model by adding InstallJson
    #       model parameter to the current model. this appears to be a pydantic
    #       issue, but more research is needed.
    # @field_validator('tc_token', mode='after')
    # @classmethod
    # def _one_set_of_credentials(cls, v, values):
    #     """Validate that one set of credentials is provided for the TC API."""
    #     _ij = InstallJson()

    #     # external Apps: require credentials and would not have an install.json file
    #     # organization (job) Apps: require credentials
    #     # playbook Apps: require credentials
    #     # service Apps: get token on createConfig message or during request
    #     if (
    #         (
    #             _ij.fqfn.is_file() is False
    #             or (_ij.model.is_playbook_app or _ij.model.is_organization_app)
    #         )
    #         and v is None
    #         and not all([values.get('tc_api_access_id'), values.get('tc_api_secret_key')])
    #     ):
    #         ex_msg = (
    #             'At least one set of ThreatConnect credentials must be provided '
    #             '(tc_api_access_id/tc_api_secret key OR tc_token/tc_token_expires).'
    #         )
    #         raise ValueError(ex_msg)
    #     return v
