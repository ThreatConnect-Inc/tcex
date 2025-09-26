"""TcEx Framework Module"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

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
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )
    tc_adv_req_exclude_null_params: bool = Field(
        default=False,
        description='Flag to exclude any null query parameters.',
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )
    tc_adv_req_fail_on_error: bool = Field(
        default=False,
        description='Flag to force fail on any error.',
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )
    tc_adv_req_headers: list[dict] | None = Field(
        None,
        description='The HTTP headers for the request.',
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )
    tc_adv_req_http_method: EditChoice | None = Field(
        None,
        description='The HTTP method for the request.',
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )
    tc_adv_req_params: list[dict] | None = Field(
        None,
        description='The HTTP query params for the request.',
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )
    tc_adv_req_path: str | None = Field(
        None,
        description='The API path for the request.',
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )
    tc_adv_req_urlencode_body: bool = Field(
        default=False,
        description='Flag to set URL encoding for the request body.',
        json_schema_extra={
            'inclusion_reason': 'feature (advancedRequest)',
            'requires_definition': True,
        },
    )

    @field_validator('tc_adv_req_headers', 'tc_adv_req_params', mode='before')
    @classmethod
    def _always_array(cls, value: list | str | None) -> list:
        """Return array value for headers and params."""
        match value:
            case list():
                return value
            case None:
                return []
            case _:
                return [value]
