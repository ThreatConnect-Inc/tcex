"""Playbook Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Field


class PlaybookModel(BaseModel):
    """Playbook Model

    Supported for the following runtimeLevel:
    * Playbook
    """

    # the KvStore context
    tc_playbook_kvstore_context: str = Field(None, alias='tc_playbook_db_context')

    # a csv list of output variables
    tc_playbook_out_variables: Optional[list]
