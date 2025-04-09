"""TcEx Framework Module"""

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ExclusionListModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='ExclusionList Model',
    validate_assignment=True,
):
    """Exclusion_List Model"""

    _associated_type = PrivateAttr(default=False)
    _cm_type = PrivateAttr(default=False)
    _shared_type = PrivateAttr(default=False)
    _staged = PrivateAttr(default=False)

    active: bool = Field(
        None,
        description='Whether the rule is active or not.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='active',
    )
    description: str | None = Field(
        None,
        allow_mutation=False,
        description='The **description** for the Exclusion_List.',
        read_only=True,
        title='description',
    )
    fixed_values: dict | None = Field(
        None,
        description='A list of exclusions represent fixed values.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fixedValues',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    managed: bool = Field(
        None,
        description='Whether the rule is managed by the system.',
        methods=['POST'],
        read_only=False,
        title='managed',
    )
    name: str | None = Field(
        None,
        description='The name of the rule.',
        methods=['POST'],
        read_only=False,
        title='name',
    )
    owner: str | None = Field(
        None,
        description='The name of the Owner of the Exclusion List.',
        methods=['POST'],
        read_only=False,
        title='owner',
    )
    owner_id: int | None = Field(
        None,
        description='The ID of the owner of this exclusion list.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='ownerId',
    )
    variable_values: dict | None = Field(
        None,
        description='A list of exclusions serve as wildcards.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='variableValues',
    )


class ExclusionListDataModel(
    BaseModel,
    title='ExclusionList Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Exclusion_Lists Data Model"""

    data: list[ExclusionListModel] | None = Field(
        [],
        description='The data for the ExclusionLists.',
        methods=['POST', 'PUT'],
        title='data',
    )


class ExclusionListsModel(
    BaseModel,
    title='ExclusionLists Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Exclusion_Lists Model"""

    _mode_support = PrivateAttr(default=False)

    data: list[ExclusionListModel] | None = Field(
        [],
        description='The data for the ExclusionLists.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


# add forward references
ExclusionListDataModel.update_forward_refs()
ExclusionListModel.update_forward_refs()
ExclusionListsModel.update_forward_refs()
