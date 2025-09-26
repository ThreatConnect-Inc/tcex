"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class VictimAssetModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='VictimAsset Model',
    validate_assignment=True,
):
    """Victim_Asset Model"""

    _associated_type: bool = PrivateAttr(default=True)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    account_name: str | None = Field(
        default=None,
        description='The network name.',
        title='accountName',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['SocialNetwork', 'NetworkAccount'],
            'conditional_required': ['SocialNetwork', 'NetworkAccount'],
            'methods': ['POST', 'PUT'],
        },
    )
    address: str | None = Field(
        default=None,
        description='The email address associated with the E-Mail Address asset.',
        title='address',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['EmailAddress'],
            'conditional_required': ['EmailAddress'],
            'methods': ['POST', 'PUT'],
        },
    )
    address_type: str | None = Field(
        default=None,
        description='The type of the E-Mail Address asset.',
        title='addressType',
        validate_default=True,
        json_schema_extra={'applies_to': ['EmailAddress'], 'methods': ['POST', 'PUT']},
    )
    associated_groups: GroupsModel | None = Field(
        default=None,
        description='A list of groups that this victim asset is associated with.',
        title='associatedGroups',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    network_type: str | None = Field(
        default=None,
        description='The type of network.',
        title='networkType',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['NetworkAccount'],
            'conditional_required': ['NetworkAccount'],
            'methods': ['POST', 'PUT'],
        },
    )
    phone: str | None = Field(
        default=None,
        description='The phone number of the asset.',
        title='phone',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['Phone'],
            'conditional_required': ['Phone'],
            'methods': ['POST', 'PUT'],
        },
    )
    social_network: str | None = Field(
        default=None,
        description='The type of social network.',
        title='socialNetwork',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['SocialNetwork'],
            'conditional_required': ['SocialNetwork'],
            'methods': ['POST', 'PUT'],
        },
    )
    type: str | None = Field(
        default=None,
        description='Type of victim asset.',
        title='type',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    victim_id: int | None = Field(
        default=None,
        description='Victim id of victim asset.',
        title='victimId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    web_link: str | None = Field(
        default=None,
        description='A link to the ThreatConnect details page for this entity.',
        frozen=True,
        title='webLink',
        validate_default=True,
    )
    website: str | None = Field(
        default=None,
        description='The website of the asset.',
        title='website',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['WebSite'],
            'conditional_required': ['WebSite'],
            'methods': ['POST', 'PUT'],
        },
    )

    @field_validator('associated_groups', mode='before')
    @classmethod
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v


class VictimAssetDataModel(
    BaseModel,
    title='VictimAsset Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Victim_Assets Data Model"""

    data: list[VictimAssetModel] | None = Field(
        [],
        description='The data for the VictimAssets.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class VictimAssetsModel(
    BaseModel,
    title='VictimAssets Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Victim_Assets Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[VictimAssetModel] | None = Field(
        [],
        description='The data for the VictimAssets.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.groups.group_model import GroupsModel
