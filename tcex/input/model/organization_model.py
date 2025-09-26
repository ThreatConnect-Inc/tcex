"""TcEx Framework Module"""

from pydantic import BaseModel, Field


class OrganizationModel(BaseModel):
    """Organization Model

    Supported for the following runtimeLevel:
    * Organization
    """

    tc_job_id: int | None = Field(
        default=None,
        description='The Job Id for the current App execution.',
        json_schema_extra={'inclusion_reason': 'runtimeLevel'},
    )
