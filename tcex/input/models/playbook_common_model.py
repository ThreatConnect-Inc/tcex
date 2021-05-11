"""Playbook Common Model"""
# third-party
from pydantic import BaseModel, Field


class PlaybookCommonModel(BaseModel):
    """Playbook Common Model

    Supported for the following runtimeLevel:
    * ApiService
    * Playbook
    * WebhookTriggerService
    * TriggerService
    """

    # the KvStore cache id (db id)
    tc_cache_kvstore_id: int = 10

    # the KvStore hostname
    tc_kvstore_host: str = Field('localhost', alias='tc_playbook_db_path')

    # the KvStore port number
    tc_kvstore_port: int = Field(6379, alias='tc_playbook_db_port')

    # the KvStore type (Redis or TCKeyValueAPI)
    tc_kvstore_type: str = Field('Redis', alias='tc_playbook_db_type')

    # the KvStore id (db id)
    tc_playbook_kvstore_id: int = 0
