"""ThreatConnect Assignee Module"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from enum import Enum
from typing import List, Optional

# third-party
from pydantic import BaseModel, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class AssigneeTypes(str, Enum):
    """Enum for install_json.params[].exposePlaybookAs"""

    Escalate = 'Escalate'
    Assigned = 'Assigned'


class TaskAssigneesModel(
    BaseModel,
    title='User Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Task Assignees Model"""

    _mode_support = PrivateAttr(True)

    data: Optional[List['TaskAssigneeModel']] = Field(
        [],
        description='The data for the Groups.',
        methods=['POST', 'PUT'],
        title='data',
    )

    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class TaskAssigneeModel(
    V3ModelABC,
    title='User Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Task Assignee Model

    "data": [
        {
            "id": 219,
            "type": "Escalate",
            "dateAdded": "2021-11-17T20:51:19Z",
            "user": {
                "id": 17,
                "userName": "user@threatconnect.com",
                "firstName": "User",
                "lastName": "Name",
                "pseudonym": "username",
                "role": "Administrator"
            }
        }
    ]
    """

    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Entity was first created.',
        read_only=True,
        title='dateAdded',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    type: Optional[AssigneeTypes] = Field(
        None,
        description='The **Type** for the Assignee.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='type',
    )
    user: Optional[UserModel] = Field(
        None,
        description='The **User Data** for the Assignee.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='user',
    )


# add forward references
TaskAssigneeModel.update_forward_refs()
TaskAssigneesModel.update_forward_refs()
