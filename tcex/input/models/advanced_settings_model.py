"""Advanced Settings Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Extra


class AdvancedSettingsModel(BaseModel):
    """Advanced Settings Model

    Feature: advancedRequest

    Supported for the following runtimeLevel:
    * Playbook
    """

    # the http body for the request
    tc_adv_req_body: Optional[any]

    # if True, exclude null parameters from query params
    tc_adv_req_exclude_null_params: bool = False

    # if True, fail on any errors encountered
    tc_adv_req_fail_on_error: bool = False

    # the http headers for the request
    tc_adv_req_headers: Optional[dict]

    # the http method for the request
    tc_adv_req_http_method: str

    # the http query parameters for the request
    tc_adv_req_params: Optional[dict]

    # the API path for the request
    tc_adv_req_path: str

    # if True, the body will be urlencoded
    tc_adv_req_urlencode_body: bool = False

    class Config:
        """DataModel Config"""

        extra = Extra.allow
        validate_assignment = True
