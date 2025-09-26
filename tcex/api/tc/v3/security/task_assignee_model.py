"""TcEx Framework Module"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, PrivateAttr
from pydantic.alias_generators import to_camel

from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class AssigneeTypes(str, Enum):
    """Enum for install_json.params[].exposePlaybookAs"""

    Escalate = 'Escalate'
    Assigned = 'Assigned'


class TaskAssigneeModel(
    V3ModelABC,
    title='User Data Model',
    alias_generator=to_camel,
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

    date_added: datetime | None = Field(
        None,
        frozen=True,
        description='The date and time that the Entity was first created.',
        # TODO: @bsummers-tc
        # read_only=True,
        title='dateAdded',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    type: AssigneeTypes | None = Field(
        None,
        description='The **Type** for the Assignee.',
        # TODO: @bsummers-tc
        # read_only=False,
        title='type',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    user: UserModel | None = Field(
        None,
        description='The **User Data** for the Assignee.',
        # TODO: @bsummers-tc
        # read_only=False,
        title='user',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class TaskAssigneesModel(
    BaseModel,
    title='User Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Task Assignees Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list['TaskAssigneeModel'] | None = Field(
        [],
        description='The data for the Groups.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )

    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# add forward references
# TaskAssigneeModel.model_rebuild()
# TaskAssigneesModel.model_rebuild()
