"""Artifact Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class Attributes(
    BaseModel,
    title='Tags Model',
):
    """Artifacts Model"""

    data: Optional[List['Attributes']] = Field(
        [],
        description='The data for the Tag.',
        title='data',
    )


class Attribute(
    BaseModel,
    title='Tag Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True
):
    type: str = Field(
        None,
        description='The **name** of the Tag.',
        methods=['POST', 'PUT'],
        title='type'
    )

    value: str = Field(
        None,
        description='The **name** of the Tag.',
        methods=['POST', 'PUT'],
        title='value'
    )

Attributes.update_forward_refs()
Attribute.update_forward_refs()
