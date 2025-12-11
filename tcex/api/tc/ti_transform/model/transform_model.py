"""Model Definition"""

from collections.abc import Callable
from typing import Annotated, Any, TypeAlias

from pydantic import BaseModel, Discriminator, Field, Tag, field_validator, model_validator

from jmespath import compile as jmespath_compile


# reusable validator
def _always_array(value: list | str) -> list[str]:
    """Return value as a list."""
    if not isinstance(value, list):
        value = [value]
    return value


class PredefinedFunctionModel(BaseModel, extra='forbid'):
    """Model Definitions"""

    name: str = Field(..., description='The name of the static method.')
    params: dict | None = Field({}, description='The parameters for the static method.')


class TransformModel(BaseModel, extra='forbid'):
    """Model Definition"""

    filter_map: dict | None = Field(None, description='')
    kwargs: dict | None = Field({}, description='')
    method: Callable | PredefinedFunctionModel | None = Field(None, description='')
    for_each: Callable | PredefinedFunctionModel | None = Field(None, description='')
    static_map: dict | None = Field(None, description='')

    @field_validator('filter_map', 'static_map', mode='before')
    @classmethod
    def _lower_map_keys(cls, v):
        """Validate static_map."""
        if isinstance(v, dict):
            v = {key.lower(): value for (key, value) in v.items()}
        return v

    # root validator that ensure at least one indicator value/summary is set
    @model_validator(mode='before')
    @classmethod
    def _required_transform(cls, v: dict):
        """Validate either static_map or method is defined."""

        fields = [v.get('filter_map'), v.get('static_map'), v.get('method'), v.get('for_each')]

        if not any(fields):
            ex_msg = 'Either map or method must be defined.'
            raise ValueError(ex_msg)

        if fields.count(None) < 2:  # noqa: PLR2004
            ex_msg = 'Only one transform mechanism can be defined.'
            raise ValueError(ex_msg)
        return v


class PathTransformModel(BaseModel, extra='forbid'):
    """."""

    default: int | str | None = Field(None, description='')
    path: str | None = Field(None, description='')

    @field_validator('path')
    @classmethod
    def _validate_path(cls, v):
        """Validate path."""
        if v is not None:
            try:
                _ = jmespath_compile(v)
            except Exception as ex:
                ex_msg = 'A valid path must be provided.'
                raise ValueError(ex_msg) from ex
        return v

    # root validator that ensure at least one indicator value/summary is set
    @model_validator(mode='before')
    @classmethod
    def _default_or_path(cls, values):
        """Validate either default or path is defined."""
        if not any([values.get('default'), values.get('path')]):
            ex_msg = 'Either default or path or both must be defined.'
            raise ValueError(ex_msg)
        return values


class MetadataTransformModel(PathTransformModel, extra='forbid'):
    """."""

    transform: list[TransformModel] | None = Field(None, description='')

    # validators
    _transform_array = field_validator('transform', mode='before')(_always_array)


class ValueTransformModel(BaseModel, extra='forbid'):
    """."""

    value: str | MetadataTransformModel


class FileOccurrenceTransformModel(BaseModel, extra='forbid'):
    """."""

    file_name: str | MetadataTransformModel | None = Field(None, description='')
    path: str | MetadataTransformModel | None = Field(None, description='')
    date: str | MetadataTransformModel | None = Field(None, description='')


class DatetimeTransformModel(PathTransformModel, extra='forbid'):
    """."""


class AssociatedGroupTransform(ValueTransformModel, extra='forbid'):
    """."""


class AssociatedIndicatorFromGroupTransform(BaseModel, extra='forbid'):
    """."""

    summary: str | MetadataTransformModel = Field(..., description='')
    indicator_type: str | MetadataTransformModel = Field(..., description='')


class AssociatedIndicatorFromIndicatorTransform(BaseModel, extra='forbid'):
    """."""

    summary: str | MetadataTransformModel = Field(..., description='')
    type: str | MetadataTransformModel = Field(..., description='')
    association_type: str | MetadataTransformModel = Field(..., description='')


class AttributeTransformModel(ValueTransformModel, extra='forbid'):
    """."""

    displayed: bool | MetadataTransformModel = Field(default=False, description='')
    source: str | MetadataTransformModel | None = Field(None, description='')
    type: str | MetadataTransformModel = Field(..., description='')
    pinned: bool | MetadataTransformModel = Field(default=False, description='')


class SecurityLabelTransformModel(ValueTransformModel, extra='forbid'):
    """."""

    color: MetadataTransformModel | None = Field(None, description='')
    description: MetadataTransformModel | None = Field(None, description='')


class TagTransformModel(ValueTransformModel, extra='forbid'):
    """."""


class TiTransformModel(BaseModel, extra='forbid'):
    """."""

    applies: Callable | None = Field(None, description='')
    associated_groups: list[AssociatedGroupTransform] = Field([], description='')
    attributes: list[AttributeTransformModel] = Field([], description='')
    date_added: DatetimeTransformModel | None = Field(None, description='')
    external_date_added: DatetimeTransformModel | None = Field(None, description='')
    external_date_expires: DatetimeTransformModel | None = Field(None, description='')
    external_last_modified: DatetimeTransformModel | None = Field(None, description='')
    first_seen: DatetimeTransformModel | None = Field(None, description='')
    last_modified: DatetimeTransformModel | None = Field(None, description='')
    last_seen: DatetimeTransformModel | None = Field(None, description='')
    security_labels: list[SecurityLabelTransformModel] = Field([], description='')
    tags: list[TagTransformModel] = Field([], description='')
    type: MetadataTransformModel = Field(..., description='')
    xid: MetadataTransformModel | None = Field(None, description='')


class GroupTransformModel(TiTransformModel, extra='forbid'):
    """."""

    associated_indicators: list[AssociatedIndicatorFromGroupTransform] = Field([], description='')

    name: MetadataTransformModel = Field(..., description='')
    # document
    malware: MetadataTransformModel | None = Field(None, description='')
    password: MetadataTransformModel | None = Field(None, description='')
    # email
    from_addr: MetadataTransformModel | None = Field(None, description='')
    score: MetadataTransformModel | None = Field(None, description='')
    to_addr: MetadataTransformModel | None = Field(None, description='')
    subject: MetadataTransformModel | None = Field(None, description='')
    body: MetadataTransformModel | None = Field(None, description='')
    header: MetadataTransformModel | None = Field(None, description='')
    # event, incident
    event_date: DatetimeTransformModel | None = Field(None, description='')
    status: MetadataTransformModel | None = Field(None, description='')
    # report
    publish_date: DatetimeTransformModel | None = Field(None, description='')
    # signature
    file_type: MetadataTransformModel | None = Field(None, description='')
    file_text: MetadataTransformModel | None = Field(None, description='')
    # document, signature
    file_name: MetadataTransformModel | None = Field(None, description='')
    # Case
    severity: MetadataTransformModel | None = Field(None, description='')


class IndicatorTransformModel(TiTransformModel, extra='forbid'):
    """."""

    associated_indicators: list[AssociatedIndicatorFromIndicatorTransform] = Field(
        [], description=''
    )
    confidence: MetadataTransformModel | None = Field(None, description='')
    rating: MetadataTransformModel | None = Field(None, description='')
    # summary: MetadataTransformModel | None = Field(None, description='')
    value1: MetadataTransformModel | None = Field(None, description='')
    value2: MetadataTransformModel | None = Field(None, description='')
    value3: MetadataTransformModel | None = Field(None, description='')
    # file
    file_occurrences: list[FileOccurrenceTransformModel] | None = Field(None, description='')
    size: MetadataTransformModel | None = Field(None, description='')
    # host
    dns_active: MetadataTransformModel | None = Field(None, description='')
    whois_active: MetadataTransformModel | None = Field(None, description='')
    active: MetadataTransformModel | None = Field(None, description='')

    # root validator that ensure at least one indicator value/summary is set
    @model_validator(mode='before')
    @classmethod
    def _one_indicator_value(cls, values):
        """Validate that at least one indicator value is provided."""

        if not any(
            [
                values.get('value1'),
                values.get('value2'),
                values.get('value3'),
            ]
        ):
            ex_msg = 'An indicator transform must be defined (e.g., value1, value2, value3).'
            raise ValueError(ex_msg)
        return values


class GroupToGroupAssociation(BaseModel, extra='forbid'):
    """."""

    xid_1: MetadataTransformModel = Field(..., description='')
    xid_2: MetadataTransformModel = Field(..., description='')


class GroupToIndicatorAssociation(BaseModel, extra='forbid'):
    """."""

    xid: MetadataTransformModel = Field(..., description='')
    indicator_value: MetadataTransformModel = Field(..., description='')
    indicator_type: MetadataTransformModel = Field(..., description='')


class IndicatorToIndicatorAssociation(BaseModel, extra='forbid'):
    """."""

    indicator_value_1: MetadataTransformModel = Field(..., description='')
    indicator_type_1: MetadataTransformModel = Field(..., description='')
    indicator_value_2: MetadataTransformModel = Field(..., description='')
    indicator_type_2: MetadataTransformModel = Field(..., description='')
    custom_association_type: MetadataTransformModel = Field(..., description='')


def get_association_discriminator(v: Any) -> str:
    """Return the association type discriminator value."""
    if isinstance(v, BaseModel):
        return v.__class__.__name__

    if 'xid_1' in v and 'xid_2' in v:
        return GroupToGroupAssociation.__name__
    if 'xid' in v and 'indicator_value' in v and 'indicator_type' in v:
        return GroupToIndicatorAssociation.__name__
    if (
        'indicator_value_1' in v
        and 'indicator_type_1' in v
        and 'indicator_value_2' in v
        and 'indicator_type_2' in v
        and 'custom_association_type' in v
    ):
        return IndicatorToIndicatorAssociation.__name__
    msg = f'Could not determine association type for {v}.'
    raise ValueError(msg)


AssociationTypes: TypeAlias = Annotated[
    Annotated[GroupToGroupAssociation, Tag(GroupToGroupAssociation.__name__)]
    | Annotated[GroupToIndicatorAssociation, Tag(GroupToIndicatorAssociation.__name__)]
    | Annotated[IndicatorToIndicatorAssociation, Tag(IndicatorToIndicatorAssociation.__name__)],
    Discriminator(get_association_discriminator),
]


class AssociationTransformModel(BaseModel, extra='forbid'):
    """."""

    applies: Callable | None = Field(None, description='')
    associations: list[AssociationTypes] = Field(default_factory=list, description='')
