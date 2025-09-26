"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class TagModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Tag Model',
    validate_assignment=True,
):
    """Tag Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=True)
    _staged: bool = PrivateAttr(default=False)

    cases: CasesModel | None = Field(
        default=None,
        description='The **cases** for the Tag.',
        frozen=True,
        title='cases',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='A brief description of the Tag.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    financial_impact: dict | None = Field(
        default=None,
        description=(
            'For ATT&CK-based tags, this is the financial impact level assigned to the tag.'
        ),
        title='financialImpact',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    groups: GroupsModel | None = Field(
        default=None,
        description='The **groups** for the Tag.',
        frozen=True,
        title='groups',
        validate_default=True,
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    indicators: IndicatorsModel | None = Field(
        default=None,
        description='The **indicators** for the Tag.',
        frozen=True,
        title='indicators',
        validate_default=True,
    )
    last_used: datetime | None = Field(
        default=None,
        description='The date and time that the Tag was last used.',
        frozen=True,
        title='lastUsed',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The **name** for the Tag.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    normalized: bool | None = Field(
        default=None,
        description=(
            'Indicates whether this tag is specified as a Main Tag within Tag Normalization.'
        ),
        frozen=True,
        title='normalized',
        validate_default=True,
    )
    owner: str | None = Field(
        default=None,
        description='The name of the Owner of the Tag.',
        title='owner',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    platforms: dict | None = Field(
        default=None,
        description='For ATT&CK-based tags, these are the platforms applicable to the technique.',
        frozen=True,
        title='platforms',
        validate_default=True,
    )
    security_coverage: dict | None = Field(
        default=None,
        description=(
            'For ATT&CK-based tags, this is the security coverage level assigned to the tag.'
        ),
        title='securityCoverage',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    synonymous_tag_names: dict | None = Field(
        default=None,
        description=(
            'For Normalized tags, this is a list of defined synonymous tag names that would '
            'normalize to this main tag.'
        ),
        frozen=True,
        title='synonymousTagNames',
        validate_default=True,
    )
    tactics: dict | None = Field(
        default=None,
        description='For ATT&CK-based tags, these are the tactics applicable to the technique.',
        frozen=True,
        title='tactics',
        validate_default=True,
    )
    technique_id: str | None = Field(
        default=None,
        description='For ATT&CK-based tags, this is the technique ID assigned to the tag.',
        frozen=True,
        title='techniqueId',
        validate_default=True,
    )
    victims: VictimsModel | None = Field(
        default=None,
        description='The **victims** for the Tag.',
        frozen=True,
        title='victims',
        validate_default=True,
    )

    @field_validator('cases', mode='before')
    @classmethod
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()  # type: ignore
        return v

    @field_validator('groups', mode='before')
    @classmethod
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @field_validator('indicators', mode='before')
    @classmethod
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()  # type: ignore
        return v

    @field_validator('victims', mode='before')
    @classmethod
    def _validate_victims(cls, v):
        if not v:
            return VictimsModel()  # type: ignore
        return v


class TagDataModel(
    BaseModel,
    title='Tag Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Tags Data Model"""

    data: list[TagModel] | None = Field(
        [],
        description='The data for the Tags.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class TagsModel(
    BaseModel,
    title='Tags Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Tags Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list[TagModel] | None = Field(
        [],
        description='The data for the Tags.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.victims.victim_model import VictimsModel
