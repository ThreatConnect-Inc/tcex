"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class SecurityLabelModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='SecurityLabel Model',
    validate_assignment=True,
):
    """Security_Label Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=True)
    _staged: bool = PrivateAttr(default=False)

    color: str | None = Field(
        default=None,
        description='Color of the security label.',
        title='color',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    date_added: datetime | None = Field(
        default=None,
        description='The date and time that the label was added.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='Description of the security label.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='Name of the security label.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    owner: str | None = Field(
        default=None,
        description='The name of the Owner of the Label.',
        title='owner',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )


class SecurityLabelDataModel(
    BaseModel,
    title='SecurityLabel Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Security_Labels Data Model"""

    data: list[SecurityLabelModel] | None = Field(
        [],
        description='The data for the SecurityLabels.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class SecurityLabelsModel(
    BaseModel,
    title='SecurityLabels Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Security_Labels Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list[SecurityLabelModel] | None = Field(
        [],
        description='The data for the SecurityLabels.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
SecurityLabelDataModel.model_rebuild()
SecurityLabelModel.model_rebuild()
SecurityLabelsModel.model_rebuild()
