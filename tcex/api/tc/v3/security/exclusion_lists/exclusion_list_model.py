"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ExclusionListModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='ExclusionList Model',
    validate_assignment=True,
):
    """Exclusion_List Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    active: bool | None = Field(
        default=None,
        description='Whether the rule is active or not.',
        title='active',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    description: str | None = Field(
        default=None,
        description='The **description** for the Exclusion_List.',
        frozen=True,
        title='description',
        validate_default=True,
    )
    fixed_values: dict | None = Field(
        default=None,
        description='A list of exclusions represent fixed values.',
        title='fixedValues',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    managed: bool | None = Field(
        default=None,
        description='Whether the rule is managed by the system.',
        title='managed',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    name: str | None = Field(
        default=None,
        description='The name of the rule.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    owner: str | None = Field(
        default=None,
        description='The name of the Owner of the Exclusion List.',
        title='owner',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    owner_id: int | None = Field(
        default=None,
        description='The ID of the owner of this exclusion list.',
        title='ownerId',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    variable_values: dict | None = Field(
        default=None,
        description='A list of exclusions serve as wildcards.',
        title='variableValues',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
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
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class ExclusionListsModel(
    BaseModel,
    title='ExclusionLists Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Exclusion_Lists Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[ExclusionListModel] | None = Field(
        [],
        description='The data for the ExclusionLists.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
ExclusionListDataModel.model_rebuild()
ExclusionListModel.model_rebuild()
ExclusionListsModel.model_rebuild()
