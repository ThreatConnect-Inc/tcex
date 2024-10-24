"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import Extra, Field

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class IntelReqTypeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Intel Requirement Type Model',
    validate_assignment=True,
):
    """Model Definition"""

    id: int | None = Field(  # pyright: ignore [reportGeneralTypeIssues]
        None,
        methods=['POST', 'PUT'],
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: str | None = Field(
        None,
        description='Name of the Intel Requirement Type.',
        read_only=True,
        title='name',
    )
    description: str | None = Field(
        None,
        description='Description of the Intel Requirement Type.',
        read_only=True,
        title='description',
    )
