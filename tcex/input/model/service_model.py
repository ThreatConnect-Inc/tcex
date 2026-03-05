"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_serializer

from tcex.input.field_type.sensitive import Sensitive


class ServiceModel(BaseModel):
    """Input Service Model

    Supported runtimeLevel:
    * ApiService
    * TriggerService
    * WebhookTriggerService
    """

    tc_svc_broker_conn_timeout: int = Field(
        default=60,
        description='The broker connection startup timeout in seconds.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel', 'requires_definition': True},
    )
    tc_svc_broker_host: str | None = Field(
        default=None,
        description='The Broker service hostname.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_broker_port: int | None = Field(
        default=None,
        description='The Broker service port number.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_broker_timeout: int = Field(
        default=60,
        description='The broker service timeout in seconds.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel', 'requires_definition': True},
    )
    tc_svc_broker_token: Sensitive | None = Field(
        default=None,
        description='The Broker auth token.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_client_topic: str | None = Field(
        default=None,
        description='The Broker client topic (App -> Core).',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_hb_timeout_seconds: int = Field(
        default=20,
        description='The heartbeat timeout interval in seconds.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_svc_id: int | None = Field(
        default=None,
        description='The unique ID for the current service.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel', 'requires_definition': True},
    )
    tc_svc_server_topic: str | None = Field(
        default=None,
        description='The Broker server topic (Core -> App).',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tcex_testing_context: str | None = Field(
        default=None,
        description='[Testing] The testing framework context.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )

    @field_serializer('tc_svc_broker_token', when_used='json')
    def convert_sensitive_to_str(self, value: Sensitive | None):
        """."""
        return str(value)
