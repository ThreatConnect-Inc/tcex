"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class SecurityLabelModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='SecurityLabel Model',
    validate_assignment=True,
):
    """Security_Label Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(True)
    _staged = PrivateAttr(False)

    color: str | None = Field(
        None,
        description='Color of the security label.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='color',
    )
    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the label was added.',
        read_only=True,
        title='dateAdded',
    )
    description: str | None = Field(
        None,
        description='Description of the security label.',
        methods=['POST', 'PUT'],
        read_only=False,
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
        description='Name of the security label.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    owner: str | None = Field(
        None,
        description='The name of the Owner of the Label.',
        methods=['POST'],
        read_only=False,
        title='owner',
    )


class SecurityLabelDataModel(
    BaseModel,
    title='SecurityLabel Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Security_Labels Data Model"""

    data: list[SecurityLabelModel] | None = Field(
        [],
        description='The data for the SecurityLabels.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SecurityLabelsModel(
    BaseModel,
    title='SecurityLabels Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Security_Labels Model"""

    _mode_support = PrivateAttr(True)

    data: list[SecurityLabelModel] | None = Field(
        [],
        description='The data for the SecurityLabels.',
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
SecurityLabelDataModel.update_forward_refs()
SecurityLabelModel.update_forward_refs()
SecurityLabelsModel.update_forward_refs()
