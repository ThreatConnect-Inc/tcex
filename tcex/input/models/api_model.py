"""API Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel


class ApiModel(BaseModel):
    """API Model

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

    # the default ThreatConnect Org for the API user [job, pb]
    api_default_org: Optional[str]

    # the API url for ThreatConnect
    tc_api_path: str = 'https://api.threatconnect.com'

    # a token for the ThreatConnect API
    # exceptions: [ApiService, TriggerService, WebhookTriggerService]
    tc_token: Optional[str]

    # the expiration epoch time for tc_token
    # exceptions: [ApiService, TriggerService, WebhookTriggerService]
    tc_token_expires: Optional[int]

    #
    # TcEx Specific
    #

    # alternate authentication credential when tc_token is not passed
    tc_api_access_id: Optional[str]

    # alternate authentication credential when tc_token is not passed
    tc_api_secret_key: Optional[str]

    # whether or not to verify the ThreatConnect API SSL cert
    tc_verify: Optional[bool] = False
