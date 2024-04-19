"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class TagModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Tag Model',
    validate_assignment=True,
):
    """Tag Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(True)
    _staged = PrivateAttr(False)

    cases: 'CasesModel' = Field(
        None,
        allow_mutation=False,
        description='The **cases** for the Tag.',
        read_only=True,
        title='cases',
    )
    description: str | None = Field(
        None,
        description='A brief description of the Tag.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='description',
    )
    groups: 'GroupsModel' = Field(
        None,
        allow_mutation=False,
        description='The **groups** for the Tag.',
        read_only=True,
        title='groups',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    indicators: 'IndicatorsModel' = Field(
        None,
        allow_mutation=False,
        description='The **indicators** for the Tag.',
        read_only=True,
        title='indicators',
    )
    last_used: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Tag was last used.',
        read_only=True,
        title='lastUsed',
    )
    name: str | None = Field(
        None,
        description='The **name** for the Tag.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    normalized: bool = Field(
        None,
        allow_mutation=False,
        description=(
            'Indicates whether this tag is specified as a Main Tag within Tag Normalization.'
        ),
        read_only=True,
        title='normalized',
    )
    owner: str | None = Field(
        None,
        description='The name of the Owner of the Tag.',
        methods=['POST'],
        read_only=False,
        title='owner',
    )
    platforms: dict | None = Field(
        None,
        allow_mutation=False,
        description='For ATT&CK-based tags, these are the platforms applicable to the technique.',
        read_only=True,
        title='platforms',
    )
    security_coverage: dict | None = Field(
        None,
        description=(
            'For ATT&CK-based tags, this is the security coverage level assigned to the tag.'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityCoverage',
    )
    synonymous_tag_names: dict | None = Field(
        None,
        allow_mutation=False,
        description=(
            'For Normalized tags, this is a list of defined synonymous tag names that would '
            'normalize to this main tag.'
        ),
        read_only=True,
        title='synonymousTagNames',
    )
    technique_id: str | None = Field(
        None,
        allow_mutation=False,
        description='For ATT&CK-based tags, this is the technique ID assigned to the tag.',
        read_only=True,
        title='techniqueId',
    )
    victims: 'VictimsModel' = Field(
        None,
        allow_mutation=False,
        description='The **victims** for the Tag.',
        read_only=True,
        title='victims',
    )

    @validator('cases', always=True, pre=True)
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()  # type: ignore
        return v

    @validator('groups', always=True, pre=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @validator('indicators', always=True, pre=True)
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()  # type: ignore
        return v

    @validator('victims', always=True, pre=True)
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
        methods=['POST', 'PUT'],
        title='data',
    )


class TagsModel(
    BaseModel,
    title='Tags Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Tags Model"""

    _mode_support = PrivateAttr(True)

    data: list[TagModel] | None = Field(
        [],
        description='The data for the Tags.',
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
from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.victims.victim_model import VictimsModel

# add forward references
TagDataModel.update_forward_refs()
TagModel.update_forward_refs()
TagsModel.update_forward_refs()
