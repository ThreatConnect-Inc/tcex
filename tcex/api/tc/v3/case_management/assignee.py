"""ThreatConnect Assignee Module"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.security.models.user_group_model import UserGroupModel
from tcex.api.tc.v3.security.models.user_model import UserModel

Assignee = Union[UserModel, UserGroupModel]
