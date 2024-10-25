"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field

# first-party
from tcex.input.field_type.sensitive import Sensitive


class PlaybookCommonModel(BaseModel):
    """Playbook Common Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * TriggerService
    * WebhookTriggerService
    """

    tc_cache_kvstore_id: int = Field(
        10,
        description='The KV Store cache DB Id.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_host: str = Field(
        'localhost',
        description='The KV Store hostname.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_pass: Sensitive | None = Field(
        None,
        description='The KV Store password.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_port: int = Field(
        6379,
        description='The KV Store port number.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_tls_enabled: bool = Field(
        False,
        description='If true, KV Store requires SSL connection.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_tls_port: int = Field(
        6379,
        description='The KV Store TLS port number.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_type: str = Field(
        'Redis',
        description='The KV Store type (Redis or TCKeyValueAPI).',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_user: str | None = Field(
        None,
        description='The KV Store username.',
        inclusion_reason='runtimeLevel',
    )
    tc_playbook_kvstore_id: int = Field(
        0,
        description='The KV Store playbook DB Id.',
        inclusion_reason='runtimeLevel',
    )
