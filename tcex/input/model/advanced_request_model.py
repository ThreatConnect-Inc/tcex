"""TcEx Framework Module"""

# pylint: disable=no-self-argument,wrong-import-position
# standard library
from typing import Any

# third-party
from pydantic import BaseModel, Field, validator

# first-party
from tcex.input.field_type import EditChoice


class AdvancedRequestModel(BaseModel):
    """Advanced Settings Model

    * why was input included -> feature (what feature?), runtime_level
    * where is input defined -> default (core), install.json

    Feature: advancedRequest

    Supported for the following runtimeLevel:
    * Playbook
    """

    tc_adv_req_body: Any | None = Field(
        None,
        description='The HTTP body for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_exclude_null_params: bool = Field(
        False,
        description='Flag to exclude any null query parameters.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_fail_on_error: bool = Field(
        False,
        description='Flag to force fail on any error.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_headers: list[dict] | None = Field(
        None,
        description='The HTTP headers for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_http_method: EditChoice = Field(
        None,
        description='The HTTP method for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_params: list[dict] | None = Field(
        None,
        description='The HTTP query params for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_path: str | None = Field(
        None,
        description='The API path for the request.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )
    tc_adv_req_urlencode_body: bool = Field(
        False,
        description='Flag to set URL encoding for the request body.',
        inclusion_reason='feature (advancedRequest)',
        requires_definition=True,
    )

    @validator('tc_adv_req_headers', 'tc_adv_req_params', always=True, pre=True)
    def _always_array(cls, value: list | str | None) -> list:
        """Return array value for headers and params."""
        match value:
            case list():
                return value
            case None:
                return []
            case _:
                return [value]
