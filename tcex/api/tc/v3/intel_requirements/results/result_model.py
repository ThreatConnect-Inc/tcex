"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ResultModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Result Model',
    validate_assignment=True,
):
    """Result Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    archived: bool | None = Field(
        default=None,
        description='Has the result been archived?',
        title='archived',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    archived_date: datetime | None = Field(
        default=None,
        description='The date and time that the Entity was archived.',
        frozen=True,
        title='archivedDate',
        validate_default=True,
    )
    associated: bool | None = Field(
        default=None,
        description='Has the result been associated to an entity within Threatconnect?',
        title='associated',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    false_positive: bool | None = Field(
        default=None,
        description='Is the result declared false positive?',
        title='falsePositive',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    intel_req_id: int | None = Field(
        default=None,
        description='The id of the intel requirement that the result is associated.',
        frozen=True,
        title='intelReqId',
        validate_default=True,
    )
    intel_requirement: dict | None = Field(
        default=None,
        description='The intel requirement associated to the result.',
        frozen=True,
        title='intelRequirement',
        validate_default=True,
    )
    internal: bool | None = Field(
        default=None,
        description='Is the result sourced internally from Threatconnect.',
        frozen=True,
        title='internal',
        validate_default=True,
    )
    item_id: int | None = Field(
        default=None,
        description='The id of the entity that matched the result.',
        frozen=True,
        title='itemId',
        validate_default=True,
    )
    item_type: str | None = Field(
        default=None,
        description='The type of the entity that matched the result.',
        frozen=True,
        title='itemType',
        validate_default=True,
    )
    matched_date: datetime | None = Field(
        default=None,
        description='The date and time that the result last matched with the intel requirement.',
        frozen=True,
        title='matchedDate',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The name of the result.',
        frozen=True,
        title='name',
        validate_default=True,
    )
    origin: str | None = Field(
        default=None,
        description='The origin of the result if derived from an internal or external source.',
        frozen=True,
        title='origin',
        validate_default=True,
    )
    owner_id: int | None = Field(
        default=None,
        description='The organization id that the result belongs.',
        frozen=True,
        title='ownerId',
        validate_default=True,
    )
    owner_name: str | None = Field(
        default=None,
        description='The organization name that the result belongs.',
        frozen=True,
        title='ownerName',
        validate_default=True,
    )
    score: int | None = Field(
        default=None,
        description='The relevancy score.',
        frozen=True,
        title='score',
        validate_default=True,
    )


class ResultDataModel(
    BaseModel,
    title='Result Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Results Data Model"""

    data: list[ResultModel] | None = Field(
        [],
        description='The data for the Results.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class ResultsModel(
    BaseModel,
    title='Results Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Results Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[ResultModel] | None = Field(
        [],
        description='The data for the Results.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
ResultDataModel.model_rebuild()
ResultModel.model_rebuild()
ResultsModel.model_rebuild()
