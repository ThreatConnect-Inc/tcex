"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class IndicatorAttributeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='IndicatorAttribute Model',
    validate_assignment=True,
):
    """Indicator_Attribute Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    created_by: UserModel | None = Field(
        default=None,
        description='The **created by** for the Indicator_Attribute.',
        frozen=True,
        title='createdBy',
        validate_default=True,
    )
    date_added: datetime | None = Field(
        default=None,
        description='The date and time that the item was first created.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    default: bool | None = Field(
        default=None,
        description=(
            'A flag indicating that this is the default attribute of its type within the object. '
            'Only applies to certain attribute and data types.'
        ),
        title='default',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    indicator: IndicatorModel | None = Field(
        default=None,
        description='Details of indicator associated with attribute.',
        frozen=True,
        title='indicator',
        validate_default=True,
    )
    indicator_id: int | None = Field(
        default=None,
        description='Indicator associated with attribute.',
        title='indicatorId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    last_modified: datetime | None = Field(
        default=None,
        description='The date and time that the Attribute was last modified.',
        frozen=True,
        title='lastModified',
        validate_default=True,
    )
    pinned: bool | None = Field(
        default=None,
        description='A flag indicating that the attribute has been noted for importance.',
        title='pinned',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    security_labels: SecurityLabelsModel | None = Field(
        default=None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        title='securityLabels',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    shard_id: int | None = Field(
        default=None,
        description='The organization of the item this Attribute is attached to.',
        frozen=True,
        title='shardId',
        validate_default=True,
    )
    source: str | None = Field(
        default=None,
        description='The attribute source.',
        title='source',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    type: str | None = Field(
        default=None,
        description='The attribute type.',
        title='type',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    value: str | None = Field(
        default=None,
        description='The attribute value.',
        title='value',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )

    @field_validator('indicator', mode='before')
    @classmethod
    def _validate_indicator(cls, v):
        if not v:
            return IndicatorModel()  # type: ignore
        return v

    @field_validator('security_labels', mode='before')
    @classmethod
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()  # type: ignore
        return v

    @field_validator('created_by', mode='before')
    @classmethod
    def _validate_user(cls, v):
        if not v:
            return UserModel()  # type: ignore
        return v


class IndicatorAttributeDataModel(
    BaseModel,
    title='IndicatorAttribute Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Indicator_Attributes Data Model"""

    data: list[IndicatorAttributeModel] | None = Field(
        [],
        description='The data for the IndicatorAttributes.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class IndicatorAttributesModel(
    BaseModel,
    title='IndicatorAttributes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Indicator_Attributes Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list[IndicatorAttributeModel] | None = Field(
        [],
        description='The data for the IndicatorAttributes.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
