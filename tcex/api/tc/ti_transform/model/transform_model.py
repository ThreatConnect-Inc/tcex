"""Model Definition"""

# standard library
from collections.abc import Callable

# third-party
from jmespath import compile as jmespath_compile
from pydantic import BaseModel, Extra, Field, root_validator, validator


# reusable validator
def _always_array(value: list | str) -> list[str]:
    """Return value as a list."""
    if not isinstance(value, list):
        value = [value]
    return value


class PredefinedFunctionModel(BaseModel, extra=Extra.forbid):
    """Model Definitions"""

    name: str = Field(..., description='The name of the static method.')
    params: dict | None = Field({}, description='The parameters for the static method.')


# pylint: disable=no-self-argument
class TransformModel(BaseModel, extra=Extra.forbid):
    """Model Definition"""

    filter_map: dict | None = Field(None, description='')
    kwargs: dict | None = Field({}, description='')
    method: Callable | PredefinedFunctionModel | None = Field(None, description='')
    for_each: Callable | PredefinedFunctionModel | None = Field(None, description='')
    static_map: dict | None = Field(None, description='')

    @validator('filter_map', 'static_map', pre=True)
    def _lower_map_keys(cls, v):
        """Validate static_map."""
        if isinstance(v, dict):
            v = {key.lower(): value for (key, value) in v.items()}
        return v

    # root validator that ensure at least one indicator value/summary is set
    @root_validator()
    def _required_transform(cls, v: dict):
        """Validate either static_map or method is defined."""

        fields = [v.get('filter_map'), v.get('static_map'), v.get('method'), v.get('for_each')]

        if not any(fields):
            raise ValueError('Either map or method must be defined.')

        if fields.count(None) < 2:
            raise ValueError('Only one transform mechanism can be defined.')
        return v


class PathTransformModel(BaseModel, extra=Extra.forbid):
    """."""

    default: str | None = Field(None, description='')
    path: str | None = Field(None, description='')

    @validator('path')
    def _validate_path(cls, v):
        """Validate path."""
        if v is not None:
            try:
                _ = jmespath_compile(v)
            except Exception:
                raise ValueError('A valid path must be provided.')
        return v

    # root validator that ensure at least one indicator value/summary is set
    @root_validator()
    def _default_or_path(cls, values):
        """Validate either default or path is defined."""
        if not any([values.get('default'), values.get('path')]):
            raise ValueError('Either default or path or both must be defined.')
        return values


class MetadataTransformModel(PathTransformModel, extra=Extra.forbid):
    """."""

    transform: list[TransformModel] | None = Field(None, description='')

    # validators
    _transform_array = validator('transform', allow_reuse=True, pre=True)(_always_array)


class ValueTransformModel(BaseModel, extra=Extra.forbid):
    """."""

    value: str | MetadataTransformModel


class FileOccurrenceTransformModel(BaseModel, extra=Extra.forbid):
    """."""

    file_name: str | MetadataTransformModel | None = Field(None, description='')
    path: str | MetadataTransformModel | None = Field(None, description='')
    date: str | MetadataTransformModel | None = Field(None, description='')


class DatetimeTransformModel(PathTransformModel, extra=Extra.forbid):
    """."""


class AssociatedGroupTransform(ValueTransformModel, extra=Extra.forbid):
    """."""


class AttributeTransformModel(ValueTransformModel, extra=Extra.forbid):
    """."""

    displayed: bool | MetadataTransformModel = Field(False, description='')
    source: str | MetadataTransformModel | None = Field(None, description='')
    type: str | MetadataTransformModel = Field(..., description='')
    pinned: bool | MetadataTransformModel = Field(False, description='')


class SecurityLabelTransformModel(ValueTransformModel, extra=Extra.forbid):
    """."""

    color: MetadataTransformModel | None = Field(None, description='')
    description: MetadataTransformModel | None = Field(None, description='')


class TagTransformModel(ValueTransformModel, extra=Extra.forbid):
    """."""


class TiTransformModel(BaseModel, extra=Extra.forbid):
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


class GroupTransformModel(TiTransformModel, extra=Extra.forbid):
    """."""

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


# pylint: disable=no-self-argument
class IndicatorTransformModel(TiTransformModel, extra=Extra.forbid):
    """."""

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
    @root_validator()
    def _one_indicator_value(cls, values):
        """Validate that one set of credentials is provided for the TC API."""

        if not any(
            [
                values.get('value1'),
                values.get('value2'),
                values.get('value3'),
            ]
        ):
            raise ValueError(
                'An indicator transform must be defined (e.g., summary, value1, value2, value3).'
            )
        return values
