"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Field


class OrganizationModel(BaseModel):
    """Organization Model

    Supported for the following runtimeLevel:
    * Organization
    """

    tc_job_id: int | None = Field(
        None,
        description='The Job Id for the current App execution.',
        inclusion_reason='runtimeLevel',
    )
