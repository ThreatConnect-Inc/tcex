"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class VictimModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Victim Model',
    validate_assignment=True,
):
    """Victim Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    assets: VictimAssetsModel | None = Field(
        default=None,
        description='A list of victim assets corresponding to the Victim.',
        title='assets',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_groups: GroupsModel | None = Field(
        default=None,
        description='A list of groups that this victim is associated with.',
        title='associatedGroups',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    attributes: VictimAttributesModel | None = Field(
        default=None,
        description='A list of Attributes corresponding to the Victim.',
        title='attributes',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    date_added: datetime | None = Field(
        default=None,
        description='The date and time that the item was first created.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='Description of the Victim.',
        frozen=True,
        title='description',
        validate_default=True,
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='Name of the Victim.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    nationality: str | None = Field(
        default=None,
        description='Nationality of the Victim.',
        title='nationality',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    org: str | None = Field(
        default=None,
        description='Org of the Victim.',
        title='org',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    owner_name: str | None = Field(
        default=None,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        frozen=True,
        title='ownerName',
        validate_default=True,
        json_schema_extra={'conditional_read_only': ['Victim']},
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
    suborg: str | None = Field(
        default=None,
        description='Suborg of the Victim.',
        title='suborg',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    tags: TagsModel | None = Field(
        default=None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        title='tags',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    web_link: str | None = Field(
        default=None,
        description='A link to the ThreatConnect details page for this entity.',
        frozen=True,
        title='webLink',
        validate_default=True,
    )
    work_location: str | None = Field(
        default=None,
        description='Work location of the Victim.',
        title='workLocation',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )

    @field_validator('associated_groups', mode='before')
    @classmethod
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @field_validator('security_labels', mode='before')
    @classmethod
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()  # type: ignore
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v

    @field_validator('assets', mode='before')
    @classmethod
    def _validate_victim_assets(cls, v):
        if not v:
            return VictimAssetsModel()  # type: ignore
        return v

    @field_validator('attributes', mode='before')
    @classmethod
    def _validate_victim_attributes(cls, v):
        if not v:
            return VictimAttributesModel()  # type: ignore
        return v


class VictimDataModel(
    BaseModel,
    title='Victim Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Victims Data Model"""

    data: list[VictimModel] | None = Field(
        [],
        description='The data for the Victims.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class VictimsModel(
    BaseModel,
    title='Victims Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Victims Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[VictimModel] | None = Field(
        [],
        description='The data for the Victims.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetsModel
from tcex.api.tc.v3.victim_attributes.victim_attribute_model import VictimAttributesModel
