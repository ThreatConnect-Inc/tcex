"""Errors for the Transform Builder."""

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ModelBase(BaseModel):
    """Model Definition"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra='forbid',
        validate_assignment=True,
        validate_by_name=True,
        validate_default=True,
    )


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
