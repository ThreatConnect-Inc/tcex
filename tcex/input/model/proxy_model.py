"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_serializer

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
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_proxy_port: int | None = Field(
        None,
        description='The proxy port number.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_proxy_username: str | None = Field(
        None,
        description='The proxy username.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_proxy_password: Sensitive | None = Field(
        None,
        description='The proxy password',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_proxy_external: bool = Field(
        default=False,
        description='Flag to enable proxy for external connections.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_proxy_tc: bool = Field(
        default=False,
        description='Flag to enable proxy for ThreatConnect connection.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )

    @field_serializer('tc_proxy_password', when_used='json')
    def convert_sensitive_to_str(self, value: Sensitive | None):
        """."""
        return str(value)
