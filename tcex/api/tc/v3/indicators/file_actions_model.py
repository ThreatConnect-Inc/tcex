"""File Actions Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class FileActionsModel(
    BaseModel,
    title='File Actions Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """File Actions Model"""

    count: Optional[int] = Field(None, description='The number of file actions.')
    data: Optional[List['FileActionModel']] = Field(
        [],
        description='The data for the File Actions.',
        methods=['POST', 'PUT'],
        title='data',
    )
    # mode: str = Field(
    #     'append',
    #     description='The PUT mode for nested objects (append, delete, replace). Default: append',
    #     methods=['POST', 'PUT'],
    #     title='append',
    # )


class FileActionModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Tag Model',
    validate_assignment=True,
):
    """File Action Model"""

    relationship: str = Field(
        ...,
        description='The File Action type.',
        methods=['POST', 'PUT'],
        title='relationship',
    )
    indicator: 'IndicatorModel' = Field(
        ...,
        description='The **indicator** related to the FileAction.',
        methods=['POST', 'PUT'],
        title='indicator',
    )


# first-party
from tcex.api.tc.v3.indicators.indicator import IndicatorModel

FileActionModel.update_forward_refs(indicator=IndicatorModel)
FileActionsModel.update_forward_refs()
