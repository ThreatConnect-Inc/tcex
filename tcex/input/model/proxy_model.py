"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field

# first-party
from tcex.input.field_type.sensitive import Sensitive


class ProxyModel(BaseModel):
    """Proxy Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * Organization
    * WebhookTriggerService
    * TriggerService
    """

    tc_proxy_host: str | None = Field(
        None,
        description='The proxy hostname.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_port: int | None = Field(
        None,
        description='The proxy port number.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_username: str | None = Field(
        None,
        description='The proxy username.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_password: Sensitive | None = Field(
        None,
        description='The proxy password',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_external: bool = Field(
        False,
        description='Flag to enable proxy for external connections.',
        inclusion_reason='runtimeLevel',
    )
    tc_proxy_tc: bool = Field(
        False,
        description='Flag to enable proxy for ThreatConnect connection.',
        inclusion_reason='runtimeLevel',
    )
