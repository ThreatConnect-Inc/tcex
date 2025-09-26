"""TcEx Framework Module"""

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class FileActionModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='File Action Model',
    validate_assignment=True,
):
    """File Action Model"""

    relationship: str = Field(
        ...,
        description='The File Action type.',
        json_schema_extra={
            'methods': ['POST', 'PUT'],
            'read_only': False,
        },
        title='relationship',
    )
    indicator: 'IndicatorModel' = Field(
        ...,
        description='The **indicator** related to the FileAction.',
        json_schema_extra={
            'methods': ['POST', 'PUT'],
            'read_only': False,
        },
        title='indicator',
    )


class FileActionsModel(
    BaseModel,
    title='File Actions Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """File Actions Model"""

    _mode_support: bool = PrivateAttr(default=True)

    count: int | None = Field(None, description='The number of file actions.')

    data: list[FileActionModel] | None = Field(
        [],
        description='The data for the File Actions.',
        json_schema_extra={
            'methods': ['POST', 'PUT'],
        },
        title='data',
    )

    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        json_schema_extra={
            'methods': ['POST', 'PUT'],
        },
        title='append',
    )


from tcex.api.tc.v3.indicators.indicator import IndicatorModel

# FileActionModel.model_rebuild()
# FileActionsModel.model_rebuild()
