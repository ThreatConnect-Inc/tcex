"""Organization Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel


class OrganizationModel(BaseModel):
    """Organization Model

    Supported for the following runtimeLevel:
    * Organization
    """

    # the current job id for the App
    tc_job_id: Optional[int]
