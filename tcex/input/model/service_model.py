"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field

# first-party
from tcex.input.field_type.sensitive import Sensitive


class ServiceModel(BaseModel):
    """Input Service Model

    Supported runtimeLevel:
    * ApiService
    * TriggerService
    * WebhookTriggerService
    """

    tc_svc_broker_conn_timeout: int = Field(
        60,
        description='The broker connection startup timeout in seconds.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_svc_broker_host: str = Field(
        None,
        description='The Broker service hostname.',
        inclusion_reason='runtimeLevel',
    )
    tc_svc_broker_port: int = Field(
        None,
        description='The Broker service port number.',
        inclusion_reason='runtimeLevel',
    )
    tc_svc_broker_timeout: int = Field(
        60,
        description='The broker service timeout in seconds.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_svc_broker_token: Sensitive = Field(
        None,
        description='The Broker auth token.',
        inclusion_reason='runtimeLevel',
    )
    tc_svc_client_topic: str = Field(
        None,
        description='The Broker client topic (App -> Core).',
        inclusion_reason='runtimeLevel',
    )
    tc_svc_hb_timeout_seconds: int = Field(
        20,
        description='The heartbeat timeout interval in seconds.',
        inclusion_reason='runtimeLevel',
    )
    tc_svc_id: int = Field(
        None,
        description='The unique ID for the current service.',
        inclusion_reason='runtimeLevel',
        requires_definition=True,
    )
    tc_svc_server_topic: str = Field(
        None,
        description='The Broker server topic (Core -> App).',
        inclusion_reason='runtimeLevel',
    )
    tcex_testing_context: str | None = Field(
        None,
        description='[Testing] The testing framework context.',
        inclusion_reason='runtimeLevel',
    )
