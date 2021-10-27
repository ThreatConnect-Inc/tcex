"""ThreatConnect Assignee Module"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel

Assignee = Union[UserModel, UserGroupModel]
