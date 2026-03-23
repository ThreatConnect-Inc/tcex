"""Errors for the Transform Builder."""

# standard library
from typing import Literal

# third-party
from pydantic import BaseModel, Extra


def snake_to_camel(snake_string: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class ModelBase(BaseModel):
    """Model definition for job.json.params"""

    class Config:
        """DataModel Config"""

        alias_generator = snake_to_camel
        validate_assignment = True
        extra = Extra.forbid


class TransformErrorCause(ModelBase):
    """Cause for an error, which should be enough information to locate the issue."""

    section: Literal[
        'Metadata', 'Associations', 'Attributes', 'File Occurrences', 'Security Labels', 'Tags'
    ]
    name: str
    index: int | None = None


class TransformError(ModelBase):
    """Structured presentation of a validation error with a transform."""

    message: str
    cause: TransformErrorCause
    definition: dict
