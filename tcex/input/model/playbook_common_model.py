"""Playbook Common Model"""
# third-party
from pydantic import BaseModel, Field


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
        alias='tc_playbook_db_path',
        description='The KV Store hostname.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_port: int = Field(
        6379,
        alias='tc_playbook_db_port',
        description='The KV Store port number.',
        inclusion_reason='runtimeLevel',
    )
    tc_kvstore_type: str = Field(
        'Redis',
        alias='tc_playbook_db_type',
        description='The KV Store type (Redis or TCKeyValueAPI).',
        inclusion_reason='runtimeLevel',
    )
    tc_playbook_kvstore_id: int = Field(
        0,
        description='The KV Store playbook DB Id.',
        inclusion_reason='runtimeLevel',
    )
