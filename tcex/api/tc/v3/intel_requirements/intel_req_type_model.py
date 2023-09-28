"""TcEx Framework Module"""
# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import BaseModel


class IntelReqTypeModel(BaseModel):
    """Model Definition"""

    name: str | None
    description: str | None
