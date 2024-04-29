"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class VictimModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Victim Model',
    validate_assignment=True,
):
    """Victim Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    assets: 'VictimAssetsModel' = Field(
        None,
        description='A list of victim assets corresponding to the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='assets',
    )
    associated_groups: 'GroupsModel' = Field(
        None,
        description='A list of groups that this victim is associated with.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    attributes: 'VictimAttributesModel' = Field(
        None,
        description='A list of Attributes corresponding to the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='attributes',
    )
    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    description: str | None = Field(
        None,
        allow_mutation=False,
        description='Description of the Victim.',
        read_only=True,
        title='description',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: str | None = Field(
        None,
        description='Name of the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    nationality: str | None = Field(
        None,
        description='Nationality of the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='nationality',
    )
    org: str | None = Field(
        None,
        description='Org of the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='org',
    )
    owner_name: str | None = Field(
        None,
        allow_mutation=False,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        read_only=True,
        title='ownerName',
    )
    security_labels: 'SecurityLabelsModel' = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityLabels',
    )
    suborg: str | None = Field(
        None,
        description='Suborg of the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='suborg',
    )
    tags: 'TagsModel' = Field(
        None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='tags',
    )
    web_link: str | None = Field(
        None,
        allow_mutation=False,
        description='A link to the ThreatConnect details page for this entity.',
        read_only=True,
        title='webLink',
    )
    work_location: str | None = Field(
        None,
        description='Work location of the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='workLocation',
    )

    @validator('associated_groups', always=True, pre=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @validator('security_labels', always=True, pre=True)
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()  # type: ignore
        return v

    @validator('tags', always=True, pre=True)
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v

    @validator('assets', always=True, pre=True)
    def _validate_victim_assets(cls, v):
        if not v:
            return VictimAssetsModel()  # type: ignore
        return v

    @validator('attributes', always=True, pre=True)
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
        methods=['POST', 'PUT'],
        title='data',
    )


class VictimsModel(
    BaseModel,
    title='Victims Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Victims Model"""

    _mode_support = PrivateAttr(False)

    data: list[VictimModel] | None = Field(
        [],
        description='The data for the Victims.',
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
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetsModel
from tcex.api.tc.v3.victim_attributes.victim_attribute_model import VictimAttributesModel

# add forward references
VictimDataModel.update_forward_refs()
VictimModel.update_forward_refs()
VictimsModel.update_forward_refs()
