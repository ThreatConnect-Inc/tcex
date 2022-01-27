"""TcEx JSON Model"""
# standard library
from typing import List, Optional, Union

# third-party
from pydantic import BaseModel, validator
from semantic_version import Version

__all__ = ['JobJsonModel']


def snake_to_camel(snake_string: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class ParamsModel(BaseModel):
    """Model for install_json.params"""

    default: Optional[Union[bool, str]]
    name: str
    prevent_updates: bool = False

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True


class JobJsonModel(BaseModel):
    """TcEx JSON Model"""

    allow_on_demand: bool = False
    enable_notifications: bool = False
    job_name: str
    notify_email: str = ''
    notify_include_log_files: bool = False
    notify_on_complete: bool = False
    notify_on_failure: bool = False
    notify_on_partial_failure: bool = False
    params: List[ParamsModel]
    program_name: str
    program_version: Version
    publish_auth: bool = False
    schedule_cron_format: str
    schedule_start_date: int
    schedule_type: str

    @validator('program_version', pre=True)
    def version(cls, v):  # pylint: disable=E0213,R0201
        """Return a version object for "version" fields."""
        if v is not None:
            return Version(v)
        return v  # pragma: no cover

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        arbitrary_types_allowed = True
        json_encoders = {Version: lambda v: str(v)}  # pylint: disable=W0108
        validate_assignment = True
