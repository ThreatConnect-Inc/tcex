"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class ResultModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Result Model',
    validate_assignment=True,
):
    """Result Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    archived: bool = Field(
        None,
        description='Has the result been archived?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='archived',
    )
    archived_date: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Entity was archived.',
        read_only=True,
        title='archivedDate',
    )
    associated: bool = Field(
        None,
        description='Has the result been associated to an entity within Threatconnect?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associated',
    )
    false_positive: bool = Field(
        None,
        description='Is the result declared false positive?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='falsePositive',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    intel_req_id: int | None = Field(
        None,
        allow_mutation=False,
        description='The id of the intel requirement that the result is associated.',
        read_only=True,
        title='intelReqId',
    )
    intel_requirement: dict | None = Field(
        None,
        allow_mutation=False,
        description='The intel requirement associated to the result.',
        read_only=True,
        title='intelRequirement',
    )
    internal: bool = Field(
        None,
        allow_mutation=False,
        description='Is the result sourced internally from Threatconnect.',
        read_only=True,
        title='internal',
    )
    item_id: int | None = Field(
        None,
        allow_mutation=False,
        description='The id of the entity that matched the result.',
        read_only=True,
        title='itemId',
    )
    item_type: str | None = Field(
        None,
        allow_mutation=False,
        description='The type of the entity that matched the result.',
        read_only=True,
        title='itemType',
    )
    matched_date: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the result last matched with the intel requirement.',
        read_only=True,
        title='matchedDate',
    )
    name: str | None = Field(
        None,
        allow_mutation=False,
        description='The name of the result.',
        read_only=True,
        title='name',
    )
    origin: str | None = Field(
        None,
        allow_mutation=False,
        description='The origin of the result if derived from an internal or external source.',
        read_only=True,
        title='origin',
    )
    owner_id: int | None = Field(
        None,
        allow_mutation=False,
        description='The organization id that the result belongs.',
        read_only=True,
        title='ownerId',
    )
    owner_name: str | None = Field(
        None,
        allow_mutation=False,
        description='The organization name that the result belongs.',
        read_only=True,
        title='ownerName',
    )
    score: int | None = Field(
        None,
        allow_mutation=False,
        description='The relevancy score.',
        read_only=True,
        title='score',
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
        methods=['POST', 'PUT'],
        title='data',
    )


class ResultsModel(
    BaseModel,
    title='Results Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Results Model"""

    _mode_support = PrivateAttr(False)

    data: list[ResultModel] | None = Field(
        [],
        description='The data for the Results.',
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
ResultDataModel.update_forward_refs()
ResultModel.update_forward_refs()
ResultsModel.update_forward_refs()
