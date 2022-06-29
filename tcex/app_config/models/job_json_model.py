"""TcEx JSON Model"""
# pylint: disable=no-self-argument,no-self-use; noqa: N805
# standard library
from typing import List, Optional, Union

# third-party
from pydantic import BaseModel, Field, validator
from semantic_version import Version

__all__ = ['JobJsonModel']


def snake_to_camel(snake_string: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class ParamsModel(BaseModel):
    """Model for jj.params"""

    default: Optional[Union[bool, str]]
    encrypt: Optional[bool] = False
    name: str
    prevent_updates: bool = False

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        # without smart_union the default value as a string of "0" would be converted to a bool
        smart_union = True
        validate_assignment = True


class JobJsonCommonModel(BaseModel):
    """Model for common field in job.json."""

    allow_on_demand: bool = Field(
        ...,
        description='If true, the job can be run on demand.',
    )
    enable_notifications: bool = Field(
        ..., description='Enables pass/fail notifications for this job.'
    )
    job_name: str
    notify_email: str = Field(
        ...,
        description='Email address to send notifications to.',
    )
    notify_include_log_files: bool = Field(
        ...,
        description='If true, the job log files will be included in the notification email.',
    )
    notify_on_complete: bool = Field(
        ...,
        description='If true, a notification will be sent when the job completes.',
    )
    notify_on_failure: bool = Field(
        ...,
        description='If true, a notification will be sent when the job fails.',
    )
    notify_on_partial_failure: bool = Field(
        ...,
        description=(
            'If true, a notification will be sent when the job completes with partial success.'
        ),
    )
    params: List[ParamsModel]
    publish_auth: bool = Field(
        ...,
        description='If true, the job will publish the authentication token.',
    )
    schedule_cron_format: str
    schedule_start_date: int
    schedule_type: str

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        arbitrary_types_allowed = True
        validate_assignment = True


class JobJsonModel(JobJsonCommonModel):
    """Model for field in job.json."""

    program_name: str
    program_version: str

    @validator('program_version')
    def version(cls, v):
        """Return a version object for "version" fields."""
        if v is not None:
            return Version(v)
        return v  # pragma: no cover

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        arbitrary_types_allowed = True
        json_encoders = {Version: lambda v: str(v)}  # pylint: disable=unnecessary-lambda
        validate_assignment = True
