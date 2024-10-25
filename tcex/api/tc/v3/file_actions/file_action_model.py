"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class FileActionModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='File Action Model',
    validate_assignment=True,
):
    """File Action Model"""

    relationship: str = Field(
        ...,
        description='The File Action type.',
        methods=['POST', 'PUT'],
        title='relationship',
        read_only=False,
    )
    indicator: 'IndicatorModel' = Field(
        ...,
        description='The **indicator** related to the FileAction.',
        methods=['POST', 'PUT'],
        title='indicator',
        read_only=False,
    )


class FileActionsModel(
    BaseModel,
    title='File Actions Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """File Actions Model"""

    _mode_support = PrivateAttr(True)

    count: int | None = Field(None, description='The number of file actions.')

    data: list[FileActionModel] | None = Field(
        [],
        description='The data for the File Actions.',
        methods=['POST', 'PUT'],
        title='data',
    )

    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


# first-party
from tcex.api.tc.v3.indicators.indicator import IndicatorModel

FileActionModel.update_forward_refs()
FileActionsModel.update_forward_refs()
