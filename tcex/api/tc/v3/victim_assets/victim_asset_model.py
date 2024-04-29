"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class VictimAssetModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='VictimAsset Model',
    validate_assignment=True,
):
    """Victim_Asset Model"""

    _associated_type = PrivateAttr(True)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    account_name: str | None = Field(
        None,
        applies_to=['SocialNetwork', 'NetworkAccount'],
        conditional_required=['SocialNetwork', 'NetworkAccount'],
        description='The network name.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='accountName',
    )
    address: str | None = Field(
        None,
        applies_to=['EmailAddress'],
        conditional_required=['EmailAddress'],
        description='The email address associated with the E-Mail Address asset.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='address',
    )
    address_type: str | None = Field(
        None,
        applies_to=['EmailAddress'],
        description='The type of the E-Mail Address asset.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='addressType',
    )
    associated_groups: 'GroupsModel' = Field(
        None,
        description='A list of groups that this victim asset is associated with.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    network_type: str | None = Field(
        None,
        applies_to=['NetworkAccount'],
        conditional_required=['NetworkAccount'],
        description='The type of network.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='networkType',
    )
    phone: str | None = Field(
        None,
        applies_to=['Phone'],
        conditional_required=['Phone'],
        description='The phone number of the asset.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='phone',
    )
    social_network: str | None = Field(
        None,
        applies_to=['SocialNetwork'],
        conditional_required=['SocialNetwork'],
        description='The type of social network.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='socialNetwork',
    )
    type: str | None = Field(
        None,
        description='Type of victim asset.',
        methods=['POST'],
        read_only=False,
        title='type',
    )
    victim_id: int | None = Field(
        None,
        description='Victim id of victim asset.',
        methods=['POST'],
        read_only=False,
        title='victimId',
    )
    web_link: str | None = Field(
        None,
        allow_mutation=False,
        description='A link to the ThreatConnect details page for this entity.',
        read_only=True,
        title='webLink',
    )
    website: str | None = Field(
        None,
        applies_to=['WebSite'],
        conditional_required=['WebSite'],
        description='The website of the asset.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='website',
    )

    @validator('associated_groups', always=True, pre=True)
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
        methods=['POST', 'PUT'],
        title='data',
    )


class VictimAssetsModel(
    BaseModel,
    title='VictimAssets Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Victim_Assets Model"""

    _mode_support = PrivateAttr(False)

    data: list[VictimAssetModel] | None = Field(
        [],
        description='The data for the VictimAssets.',
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

# add forward references
VictimAssetDataModel.update_forward_refs()
VictimAssetModel.update_forward_refs()
VictimAssetsModel.update_forward_refs()
