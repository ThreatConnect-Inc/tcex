"""TcEx Framework Module"""

from pydantic import Field

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class IntelReqTypeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Intel Requirement Type Model',
    validate_assignment=True,
):
    """Model Definition"""

    id: int | None = Field(  # pyright: ignore [reportGeneralTypeIssues]
        None,
        json_schema_extra={'methods': ['POST', 'PUT'], 'read_only': True},
        description='The ID of the item.',
        title='id',
    )
    name: str | None = Field(
        None,
        description='Name of the Intel Requirement Type.',
        json_schema_extra={'methods': ['POST', 'PUT'], 'read_only': True},
        title='name',
    )
    description: str | None = Field(
        None,
        description='Description of the Intel Requirement Type.',
        json_schema_extra={'methods': ['POST', 'PUT'], 'read_only': True},
        title='description',
    )
