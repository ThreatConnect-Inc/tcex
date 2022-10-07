"""Transform Abstract Base Class"""
# standard library
import logging
from abc import ABC, abstractmethod
from inspect import signature
from typing import TYPE_CHECKING, List, Optional, Union

# third-party
import jmespath
from pydantic import ValidationError

# first-party
from tcex.api.tc.ti_transform.model import GroupTransformModel, IndicatorTransformModel
from tcex.utils import Utils

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.ti_transform.model import (
        AttributeTransformModel,
        MetadataTransformModel,
        SecurityLabelTransformModel,
        TagTransformModel,
    )

# get tcex logger
logger = logging.getLogger('tcex')


class TransformsABC(ABC):
    """Transform Abstract Base Class"""

    def __init__(
        self,
        ti_dicts: List[dict],
        transforms: List[Union['GroupTransformModel', 'IndicatorTransformModel']],
    ):
        """Initialize class properties."""
        self.ti_dicts = ti_dicts
        self.transforms = transforms

        # properties
        self.log = logger
        self.transformed_collection = []

        # validate transforms
        self._validate_transforms()

    def _validate_transforms(self):
        """Validate the transform model."""
        if len(self.transforms) > 1:
            for transform in self.transforms:
                if transform.applies is None:
                    raise ValidationError(
                        'If more than one transform is provided, each '
                        'provided transform must provide an apply field.'
                    )


class TransformABC(ABC):
    """Transform Abstract Base Class"""

    def __init__(
        self,
        ti_dict: dict,
        transforms: List[Union['GroupTransformModel', 'IndicatorTransformModel']],
    ):
        """Initialize class properties."""
        self.ti_dict = ti_dict
        self.transforms = transforms

        # properties
        self.log = logger
        # self.ti_type = None
        self.transform = None  # the current active transform
        self.transformed_item = {}
        self.utils = Utils()

        # validate transforms
        self._validate_transforms()

    @staticmethod
    def _always_array(value: Union[str, list]) -> list:
        """Ensure value is always an array."""
        if not isinstance(value, list):
            value = [value]
        return value

    @staticmethod
    def _build_summary(
        val1: Optional[str] = None, val2: Optional[str] = None, val3: Optional[str] = None
    ) -> str:
        """Build the Indicator summary using available values."""
        return ' : '.join([value for value in [val1, val2, val3] if value is not None])

    def _path_search(self, path: str) -> any:
        """Return the value of the provided path.

        Path can return any type of data from the TI dict.
        """
        if path is not None:
            return jmespath.search(path, self.ti_dict)
        return None

    def _process(self):
        """Process the TI data."""
        # choose the correct transform model before processing TI data
        self._select_transform()

        # process type first, fail early
        self._process_type()

        # process type specific data
        if isinstance(self.transform, GroupTransformModel):
            self._process_group()
        elif isinstance(self.transform, IndicatorTransformModel):
            self._process_indicator()

        # self.process_associations(self.transform.associations)
        self._process_associated_group(self.transform.associated_groups)
        self._process_attributes(self.transform.attributes or [])
        self._process_security_labels(self.transform.security_labels or [])
        self._process_tags(self.transform.tags or [])

        # date added
        self._process_metadata_datetime('dateAdded', self.transform.date_added)

        # last modified
        self._process_metadata_datetime('lastModified', self.transform.last_modified)

        # xid
        self._process_metadata('xid', self.transform.xid)

    def _process_associated_group(self, associations: List['AttributeTransformModel']):
        """Process Attribute data"""
        for association in associations or []:
            for value in self._transform_values(association):
                self.add_associated_group(value)

    def _process_attributes(self, attributes: List['AttributeTransformModel']):
        """Process Attribute data"""
        for attribute in attributes or []:
            for value in self._transform_values(attribute):
                if value == 'Target Country':
                    print('!!!!', value)
                self.add_attribute(
                    displayed=attribute.displayed,
                    source=self._transform_value(attribute.source),
                    type_=attribute.type,
                    value=str(value),
                )

    def _process_confidence(self, metadata: 'MetadataTransformModel'):
        """Process standard metadata fields."""
        self.add_confidence(self._transform_value(metadata))

    def _process_group(self):
        """Process Group Specific data."""
        self._process_name()

        if self.transformed_item['type'] == 'Campaign':
            self._process_metadata('firstSeen', self.transform.first_seen)

        if self.transformed_item['type'] == 'Document':
            self._process_metadata('fileName', self.transform.file_name)
            self._process_metadata('malware', self.transform.malware)
            self._process_metadata('password', self.transform.confidence)

        if self.transformed_item['type'] == 'Email':
            self._process_metadata('from', self.transform.from_addr)
            self._process_metadata('to', self.transform.to_addr)

        if self.transformed_item['type'] in ('Event', 'Incident'):
            self._process_metadata('eventDate', self.transform.event_date)
            self._process_metadata('status', self.transform.status)

        if self.transformed_item['type'] == 'Report':
            self._process_metadata('fileName', self.transform.file_name)
            self._process_metadata_datetime('publishDate', self.transform.publish_date)

    def _process_indicator(self):
        """Process Indicator Specific data."""
        # handle the 3 possible indicator fields
        self._process_indicator_values()

        self._process_confidence(self.transform.confidence)
        self._process_rating(self.transform.rating)

        if self.transformed_item['type'] == 'File':
            self._process_metadata('size', self.transform.size)

        if self.transformed_item['type'] == 'Host':
            self._process_metadata('dnsActive', self.transform.dns_active)
            self._process_metadata('whoisActive', self.transform.whois_active)

    def _process_indicator_values(self):
        value1 = self._transform_value(self.transform.value1)
        value2 = self._transform_value(self.transform.value2)
        value3 = self._transform_value(self.transform.value3)

        if not any([value1, value2, value3]):
            self.log.error(
                'feature=ti-transform, event=process-indicators, message=no-indicator-value-found, '
                f'path-value1={self.transform.value1.path}'
                f'path-value2={self.transform.value2.path}'
                f'path-value3={self.transform.value3.path}'
            )
            raise RuntimeError('At least one indicator value must be provided.')

        self.add_summary(self._build_summary(value1, value2, value3))

    def _process_name(self):
        name = self._transform_value(self.transform.name)

        if name is None:
            self.log.error(
                'feature=ti-transform, event=process-group-name, message=no-name-found, '
                f'path={self.transform.name.path}'
            )
            raise RuntimeError('At least one indicator value must be provided.')

        self.add_name(name)

    def _process_metadata(self, key, metadata: 'MetadataTransformModel'):
        """Process standard metadata fields."""
        value = self._transform_value(metadata)
        if value is not None:
            self.add_metadata(key, value)

    def _process_metadata_datetime(self, key, metadata: List['MetadataTransformModel']):
        """Process metadata fields that should be a TC datetime."""
        if metadata is not None:
            value = self._path_search(metadata.path)
            if value is not None:
                self.add_metadata(
                    key, self.utils.any_to_datetime(value).strftime('%Y-%m-%dT%H:%M:%SZ')
                )

    def _process_security_labels(self, labels: List['SecurityLabelTransformModel']):
        """Process Tag data"""
        for label in labels or []:
            for value in self._transform_values(label):
                self.add_security_label(
                    color=self._transform_value(label.color),
                    description=self._transform_value(label.description),
                    name=value,
                )

    def _process_tags(self, tags: List['TagTransformModel']):
        """Process Tag data"""
        for tag in tags or []:
            for value in self._transform_values(tag):
                self.add_tag(name=value)

    def _process_rating(self, metadata: 'MetadataTransformModel'):
        """Process standard metadata fields."""
        self.add_rating(self._transform_value(metadata))

    def _process_type(self):
        """Process standard metadata fields."""
        _type = self._transform_value(self.transform.type)
        if _type is not None:
            self.transformed_item['type'] = _type
        else:
            self.log.error(
                'feature=ti-transform, action=process-type, error=invalid=type, '
                f'path={self.transform.type.path}, value={_type}'
            )
            raise RuntimeError('Invalid type')

    def _select_transform(self):
        """Select the correct transform based on the "applies" field."""
        for transform in self.transforms:
            if transform.applies is None or transform.applies(self.ti_dict) is True:
                self.transform = transform
                break
        else:
            raise RuntimeError('No transform found for TI data')

    def _transform_value(self, metadata: Optional['MetadataTransformModel']) -> Optional[str]:
        """Pass value to series transforms."""
        # not all fields are required
        if metadata is None:
            return None

        # not all metadata fields have a path, but they must have a path or default
        if metadata.path is None:
            return metadata.default

        # get value from path
        value = self._path_search(metadata.path)

        # return default if value of None is returned from Path
        # IMPORTANT: a value of None passed to the transform may cause a failure (lambda x.lower())
        if value is None:
            return metadata.default

        for t in metadata.transform or []:
            # pass value to static_map or callable, but never both
            if t.filter_map is not None:
                self._transform_value_map(t.filter_map, value, True)
            elif t.static_map is not None:
                self._transform_value_map(t.static_map, value)
            elif callable(t.method):
                value = self._transform_value_callable(value, t)

        # ensure only a string value or None is returned (set to default if required)
        if value is None:
            value = metadata.default
        elif not isinstance(value, str):
            value = str(value)

        return value

    def _transform_value_callable(
        self, value: Union[dict, list, str], t: 'MetadataTransformModel'
    ) -> Union[Optional[str], Optional[List[str]]]:
        """Transform values in the TI data."""
        # find signature of method and call with correct args
        sig = signature(t.method, follow_wrapped=True)
        if 'ti_dict' in sig.parameters:
            t.kwargs.update({'ti_dict': self.ti_dict})

        # pass value to transform callable/method, which should always return a string
        return t.method(value, **t.kwargs)

    def _transform_value_map(self, value: str, map_: dict, passthrough: bool = False) -> str:
        """Transform a value using a static map."""
        _default = value if passthrough is True else None
        if isinstance(value, str):
            # a static map is a dict of key/value pairs
            value = map_.get(value.lower(), _default)
        else:
            self.log.warning(
                f'''feature=ti-transform, action=transform-value, '''
                f'''message='static-map-requires-str-value", value={value}'''
            )
        return value

    def _transform_values(self, metadata: Optional['MetadataTransformModel']) -> List[str]:
        """Pass value to series transforms."""

        def _default() -> str:
            """Return default value (as list) if exists, else empty list."""
            if metadata.default is None:
                return []
            return self._always_array(metadata.default)

        # not all items have all metadata fields
        if metadata is None:
            return []

        # not all metadata fields have a path, but they must have a path or default
        if metadata.path is None:
            return _default()

        # path search can return multiple data types and single or multiple values
        value = self._path_search(metadata.path)

        # return default if value of None is returned from Path
        # IMPORTANT: a None value passed to the transform may cause a failure (lambda x: x.lower())
        if value in [None, []]:
            return _default()

        for t in metadata.transform or []:
            if t.filter_map is not None:
                # when path search returns an array of values, each value is mapped
                value = [
                    self._transform_value_map(v, t.filter_map, True)
                    for v in self._always_array(value)
                ]
            elif t.static_map is not None:
                # when path search returns an array of values, each value is mapped
                value = [
                    self._transform_value_map(v, t.static_map) for v in self._always_array(value)
                ]
            elif callable(t.method):
                value = self._transform_value_callable(value, t)

        # the output should be an array of strings or empty array
        _value = []
        for v in self._always_array(value):
            if v in [None, '']:
                if metadata.default is not None:
                    _value.append(metadata.default)
            else:
                _value.append(v)

        return _value

    def _validate_transforms(self):
        """Validate the transform model."""
        if len(self.transforms) > 1:
            for transform in self.transforms:
                if transform.applies is None:
                    raise ValidationError(
                        'If more than one transform is provided, each '
                        'provided transform must provide an apply field.'
                    )

    @abstractmethod
    def add_associated_group(self, group_xid: str):
        """Abstract method"""

    @abstractmethod
    def add_attribute(
        self,
        type_: str,
        value: str,
        displayed: Optional[bool] = False,
        source: Optional[str] = None,
    ):
        """Abstract method"""

    @abstractmethod
    def add_confidence(self, confidence: Optional[int]):
        """Abstract method"""

    @abstractmethod
    def add_metadata(self, key: str, value: str):
        """Abstract method"""

    @abstractmethod
    def add_name(self, name: Optional[str]):
        """Abstract method"""

    @abstractmethod
    def add_rating(self, rating: Optional[int]):
        """Abstract method"""

    @abstractmethod
    def add_security_label(
        self, name: str, color: Optional[str] = None, description: Optional[str] = None
    ):
        """Abstract method"""

    @abstractmethod
    def add_summary(self, value: Optional[str]):
        """Abstract method"""

    @abstractmethod
    def add_tag(self, name: str):
        """Abstract method"""
