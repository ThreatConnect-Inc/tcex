"""TcEx Framework Module"""

from pydantic import BaseModel, Field, field_serializer

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
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_kvstore_host: str = Field(
        'localhost',
        description='The KV Store hostname.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_kvstore_pass: Sensitive | None = Field(
        None,
        description='The KV Store password.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_kvstore_port: int = Field(
        6379,
        description='The KV Store port number.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_kvstore_tls_enabled: bool = Field(
        default=False,
        description='If true, KV Store requires SSL connection.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_kvstore_tls_port: int = Field(
        6379,
        description='The KV Store TLS port number.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_kvstore_type: str = Field(
        'Redis',
        description='The KV Store type (Redis or TCKeyValueAPI).',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_kvstore_user: str | None = Field(
        None,
        description='The KV Store username.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
    tc_playbook_kvstore_id: int = Field(
        0,
        description='The KV Store playbook DB Id.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )

    @field_serializer('tc_kvstore_pass', when_used='json')
    def convert_sensitive_to_str(self, value: Sensitive | None):
        """."""
        return str(value)
