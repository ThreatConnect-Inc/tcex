"""Model Definition"""
# standard library
from typing import Callable, List, Optional, Union

# third-party
from jmespath import compile as jmespath_compile
from pydantic import BaseModel, Extra, Field, root_validator, validator


# reusable validator
def _always_array(value: Union[list, str]) -> List[str]:
    """Return value as a list."""
    if not isinstance(value, list):
        value = [value]
    return value


# pylint: disable=no-self-argument, no-self-use
class TransformModel(BaseModel, extra=Extra.forbid):
    """Model Definition"""

    filter_map: Optional[dict] = Field(None, description='')
    kwargs: Optional[dict] = Field({}, description='')
    method: Optional[Callable] = Field(None, description='')
    for_each: Optional[Callable] = Field(None, description='')
    static_map: Optional[dict] = Field(None, description='')

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

    default: Optional[str] = Field(None, description='')
    path: Optional[str] = Field(None, description='')

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

    transform: Optional[List[TransformModel]] = Field(None, description='')

    # validators
    _transform_array = validator('transform', allow_reuse=True, pre=True)(_always_array)


class ValueTransformModel(BaseModel, extra=Extra.forbid):
    """."""

    value: Union[str, MetadataTransformModel]


class FileOccurrenceTransformModel(BaseModel, extra=Extra.forbid):
    """."""

    file_name: Optional[Union[str, MetadataTransformModel]] = Field(None, description='')
    path: Optional[Union[str, MetadataTransformModel]] = Field(None, description='')
    date: Optional[Union[str, MetadataTransformModel]] = Field(None, description='')


class DatetimeTransformModel(PathTransformModel, extra=Extra.forbid):
    """."""


class AssociatedGroupTransform(ValueTransformModel, extra=Extra.forbid):
    """."""


class AttributeTransformModel(ValueTransformModel, extra=Extra.forbid):
    """."""

    displayed: Union[bool, MetadataTransformModel] = Field(False, description='')
    source: Optional[Union[str, MetadataTransformModel]] = Field(None, description='')
    type: Union[str, MetadataTransformModel] = Field(..., description='')


class SecurityLabelTransformModel(ValueTransformModel, extra=Extra.forbid):
    """."""

    color: Optional[MetadataTransformModel] = Field(None, description='')
    description: Optional[MetadataTransformModel] = Field(None, description='')


class TagTransformModel(ValueTransformModel, extra=Extra.forbid):
    """."""


class TiTransformModel(BaseModel, extra=Extra.forbid):
    """."""

    applies: Optional[Callable] = Field(None, description='')
    associated_groups: Optional[List[AssociatedGroupTransform]] = Field(None, description='')
    attributes: Optional[List[AttributeTransformModel]] = Field(None, description='')
    date_added: Optional[DatetimeTransformModel] = Field(None, description='')
    last_modified: Optional[DatetimeTransformModel] = Field(None, description='')
    security_labels: Optional[List[SecurityLabelTransformModel]] = Field(None, description='')
    tags: Optional[List[TagTransformModel]] = Field(None, description='')
    type: MetadataTransformModel = Field(..., description='')
    xid: Optional[MetadataTransformModel] = Field(description='')


class GroupTransformModel(TiTransformModel, extra=Extra.forbid):
    """."""

    name: MetadataTransformModel = Field(..., description='')
    # campaign
    first_seen: Optional[DatetimeTransformModel] = Field(None, description='')
    # document
    malware: Optional[MetadataTransformModel] = Field(None, description='')
    password: Optional[MetadataTransformModel] = Field(None, description='')
    # email
    from_addr: Optional[MetadataTransformModel] = Field(None, description='')
    score: Optional[MetadataTransformModel] = Field(None, description='')
    to_addr: Optional[MetadataTransformModel] = Field(None, description='')
    subject: Optional[MetadataTransformModel] = Field(None, description='')
    body: Optional[MetadataTransformModel] = Field(None, description='')
    header: Optional[MetadataTransformModel] = Field(None, description='')
    # event, incident
    event_date: Optional[DatetimeTransformModel] = Field(None, description='')
    status: Optional[MetadataTransformModel] = Field(None, description='')
    # report
    publish_date: Optional[DatetimeTransformModel] = Field(None, description='')
    # signature
    file_type: Optional[MetadataTransformModel] = Field(None, description='')
    file_text: Optional[MetadataTransformModel] = Field(None, description='')
    # document, signature
    file_name: Optional[MetadataTransformModel] = Field(None, description='')


# pylint: disable=no-self-argument,no-self-use
class IndicatorTransformModel(TiTransformModel, extra=Extra.forbid):
    """."""

    confidence: Optional[MetadataTransformModel] = Field(None, description='')
    rating: Optional[MetadataTransformModel] = Field(None, description='')
    # summary: Optional[MetadataTransformModel] = Field(None, description='')
    value1: Optional[MetadataTransformModel] = Field(None, description='')
    value2: Optional[MetadataTransformModel] = Field(None, description='')
    value3: Optional[MetadataTransformModel] = Field(None, description='')
    # file
    file_occurrences: Optional[List[FileOccurrenceTransformModel]] = Field(None, description='')
    size: Optional[MetadataTransformModel] = Field(None, description='')
    # host
    dns_active: Optional[MetadataTransformModel] = Field(None, description='')
    whois_active: Optional[MetadataTransformModel] = Field(None, description='')
    active: Optional[MetadataTransformModel] = Field(None, description='')

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
