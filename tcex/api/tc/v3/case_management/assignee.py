"""ThreatConnect Assignee Module"""
# standard library
from typing import Union

# first-party
from tcex.security.models.user_group_model import UserGroupModel
from tcex.security.models.user_model import UserModel

Assignee = Union[UserModel, UserGroupModel]
