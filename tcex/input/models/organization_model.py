"""Organization Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Field


class OrganizationModel(BaseModel):
    """Organization Model

    Supported for the following runtimeLevel:
    * Organization
    """

    tc_job_id: Optional[int] = Field(
        None,
        description='The Job Id for the current App execution.',
        inclusion_reason='runtimeLevel',
    )
