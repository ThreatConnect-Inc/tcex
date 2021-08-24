"""Proxy Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Field

# first-party
from tcex.input.field_types.sensitive import Sensitive


class ProxyModel(BaseModel):
    """Proxy Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    tc_proxy_host: Optional[str] = Field(
        None,
        description='The proxy hostname.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_port: Optional[int] = Field(
        None,
        description='The proxy port number.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_username: Optional[str] = Field(
        None,
        description='The proxy username.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_password: Optional[Sensitive] = Field(
        None,
        description='The proxy password',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_external: Optional[bool] = Field(
        False,
        description='Flag to enable proxy for external connections.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_tc: Optional[bool] = Field(
        False,
        description='Flag to enable proxy for ThreatConnect connection.',
        inclusion_reason='runtimeLevel',
    )
