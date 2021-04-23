"""Install JSON Model"""
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, validator
from semantic_version import Version


class TemplateConfigModel(BaseModel):
    """App Template Config Model."""

    contributor: str
    description: str
    name: str
    summary: str
    template_files: List[str]
    template_parents: Optional[List[str]] = []
    type: str
    version: Version

    @validator('version', pre=True)
    def version_validator(cls, v):  # pylint: disable=E0213,R0201
        """Return a version object for "version" fields."""
        if v is not None:
            return Version(v)
        return v

    class Config:
        """DataModel Config"""

        arbitrary_types_allowed = True
        json_encoders = {Version: lambda v: str(v)}  # pylint: disable=W0108
        validate_assignment = True
