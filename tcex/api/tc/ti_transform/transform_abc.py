"""Transform Abstract Base Class"""
# standard library
import collections
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from inspect import signature
from typing import TYPE_CHECKING, Callable, List, Optional, Union

# third-party
import jmespath
from jmespath import functions
from pydantic import ValidationError

# first-party
from tcex.api.tc.ti_transform.model import (
    GroupTransformModel,
    IndicatorTransformModel,
    MetadataTransformModel,
)
from tcex.utils import Utils

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.ti_transform.model import (
        AttributeTransformModel,
        SecurityLabelTransformModel,
        TagTransformModel,
    )

# get tcex logger
logger = logging.getLogger('tcex')


class TcFunctions(functions.Functions):
    """ThreatConnect custom jmespath functions."""

    @functions.signature({'types': ['array']}, {'types': ['string']})
    def _func_null_leaf(self, arr, search):  # pylint: disable=no-self-use
        """Return value in array even if they are null.

        Arguments:
            arr (list) - a list of objects (dict).
            search (string) - the dict key to retrieve.

        Returns:
            list - A list of results, including null values.

        """
        return [a.get(search) for a in arr]

    @functions.signature({'types': ['array']}, {'types': ['string']})
    def _func_delete(self, arr, search):  # pylint: disable=no-self-use
        """Return array after popping value at address out.

        Arguments:
            arr (list) - a list of objects (dict).
            search (string) - the dict key to delete.

        Returns:
            list - The provided arr with the keys removed

        """
        for a in arr:
            try:
                a.pop(search)
            except Exception:
                print('Skipping delete, field not found.')
        return arr


class TransformsABC(ABC):
    """Transform Abstract Base Class"""

    def __init__(
        self,
        ti_dicts: List[dict],
        transforms: List[Union['GroupTransformModel', 'IndicatorTransformModel']],
    ):
        """Initialize class properties."""
        self.ti_dicts = ti_dicts
        self.transforms = transforms if isinstance(transforms, list) else [transforms]

        # properties
        self.log = logger
        self.transformed_collection: List['TransformABC'] = []

        # validate transforms
        self._validate_transforms()

    def _validate_transforms(self):
        """Validate the transform model."""
        if len(self.transforms) > 1:
            for transform in self.transforms:
                if transform.applies is None:
                    raise ValidationError(
                        'If more than one transform is provided, each '
                        'provided transform must provide an apply field.',
                        None,
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
        self.transforms = transforms if isinstance(transforms, list) else [transforms]

        # properties
        self.adhoc_groups: List[dict] = []
        self.adhoc_indicators: List[dict] = []
        self.log = logger
        # the current active transform
        self.transform: Union['GroupTransformModel', 'IndicatorTransformModel'] = None
        self.transformed_item = {}
        self.utils = Utils()
        self.jmespath_options = jmespath.Options(
            custom_functions=TcFunctions(), dict_cls=collections.OrderedDict
        )

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
            value = jmespath.search(path, self.ti_dict, options=self.jmespath_options)
            # self.log.trace(f'feature=transform, action=path-search, path={path}, value={value}')
            return value
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
            for value in filter(bool, self._process_metadata_transform_model(association.value)):
                self.add_associated_group(value)

    def _process_metadata_transform_model(
        self, value: Union['MetadataTransformModel', str], expected_length: Optional[int] = None
    ) -> List:
        """Process fields that can be static values or a MetadataTransformModel.

        If value is not a MetadataTransformModel (i.e., it's a static value), and expected_length
        is given, "spread" the static value into an array of expected_length length.

        """
        if isinstance(value, MetadataTransformModel):
            transformed_value = self._transform_values(value)

            if expected_length is not None and len(transformed_value) != expected_length:
                raise RuntimeError(
                    f'Expected transform value of length {expected_length} for {value}, '
                    f'but length was {len(transformed_value)}'
                )

            # self.log.trace(
            #     'feature=transform, action=process-metadata-transform-model, '
            #     f'value-path={value.path}, transformed-value={transformed_value}'
            # )
            return transformed_value

        if expected_length is not None:
            transformed_value = [value] * expected_length
        else:
            transformed_value = [value]

        # self.log.trace(
        #     'feature=transform, action=process-metadata-transform-data, '
        #     f'value={value}, transformed-value={transformed_value}'
        # )
        return transformed_value

    def _process_attributes(self, attributes: List['AttributeTransformModel']):
        """Process Attribute data"""
        for attribute in attributes or []:
            values = self._process_metadata_transform_model(attribute.value)
            if not values:
                # self.log.info(f'No values found for attribute transform {attribute.dict()}')
                continue

            types = self._process_metadata_transform_model(attribute.type, len(values))
            source = self._process_metadata_transform_model(attribute.source, len(values))
            displayed = self._process_metadata_transform_model(attribute.displayed, len(values))

            param_keys = ['type_', 'value', 'displayed', 'source']
            params = [dict(zip(param_keys, p)) for p in zip(types, values, displayed, source)]

            for param in params:
                param = self.utils.remove_none(param)
                if 'value' not in param:
                    continue

                if 'type_' not in param:
                    self.log.warning(
                        'feature=transform, action=process-attribute, '
                        f'transform={attribute.dict(exclude_unset=True)}, error=no-type'
                    )
                    continue

                # strip out None params so that required params are enforced and optional
                # params with default values are respected.
                try:
                    self.add_attribute(**param)
                except Exception:
                    self.log.exception(
                        'feature=transform, action=process-attribute, '
                        f'transform={attribute.dict(exclude_unset=True)}'
                    )

    def _process_file_occurrences(self, file_occurrences: List['MetadataTransformModel']):
        """Process File Occurrences data.

        File Occurrences are a bit weird, in that none of the fields are required.  Because of this,
        There may be results where all of the fields are None, in which case we'll skip that result
        and not call add_file_occurrence.
        """
        for file_occurrence in file_occurrences or []:
            expected_length = max(
                map(
                    lambda f: len(self._process_metadata_transform_model(f)),
                    [
                        field
                        for field in (
                            file_occurrence.file_name,
                            file_occurrence.path,
                            file_occurrence.date,
                        )
                        if field is not None
                    ],
                )
            )
            file_name = self._process_metadata_transform_model(
                file_occurrence.file_name, expected_length
            )
            path = self._process_metadata_transform_model(file_occurrence.path, expected_length)
            date = self._process_metadata_transform_model(file_occurrence.date, expected_length)

            param_keys = ['file_name', 'path', 'date']
            params = [dict(zip(param_keys, p)) for p in zip(file_name, path, date)]

            for kwargs in filter(bool, params):  # get rid of empty dicts
                self.add_file_occurrence(**self.utils.remove_none(kwargs))

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
            self._process_metadata('subject', self.transform.subject)
            self._process_metadata('body', self.transform.body)
            self._process_metadata('header', self.transform.header)

        if self.transformed_item['type'] in ('Event', 'Incident'):
            self._process_metadata_datetime('eventDate', self.transform.event_date)
            self._process_metadata('status', self.transform.status)

        if self.transformed_item['type'] == 'Report':
            self._process_metadata('fileName', self.transform.file_name)
            self._process_metadata_datetime('publishDate', self.transform.publish_date)

        # Handle sig specific fields here
        if self.transformed_item['type'] == 'Signature':
            self._process_metadata('fileName', self.transform.file_name)
            self._process_metadata('fileType', self.transform.file_type)
            self._process_metadata('fileText', self.transform.file_text)

    def _process_indicator(self):
        """Process Indicator Specific data."""
        # handle the 3 possible indicator fields
        self._process_indicator_values()

        if self.transform.active:
            self._process_metadata('active', self.transform.active)

        self._process_confidence(self.transform.confidence)
        self._process_rating(self.transform.rating)

        if self.transformed_item['type'] == 'File':
            self._process_metadata('size', self.transform.size)
            self._process_file_occurrences(self.transform.file_occurrences or [])

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
            names = self._process_metadata_transform_model(label.value)
            if not names:
                # self.log.info(f'No values found for security label transform {label.dict()}')
                continue

            descriptions = self._process_metadata_transform_model(
                label.description, expected_length=len(names)
            )
            colors = self._process_metadata_transform_model(label.color, expected_length=len(names))

            param_keys = ['color', 'description', 'name']
            params = [dict(zip(param_keys, p)) for p in zip(colors, descriptions, names)]

            for kwargs in params:
                kwargs = self.utils.remove_none(kwargs)
                if 'name' not in kwargs:
                    continue
                # strip out None params so that required params are enforced and optional
                # params with default values are respected.
                self.add_security_label(**kwargs)

    def _process_tags(self, tags: List['TagTransformModel']):
        """Process Tag data"""
        for tag in tags or []:
            for value in filter(bool, self._process_metadata_transform_model(tag.value)):
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
                value = self._transform_value_map(value, t.filter_map, True)
            elif t.static_map is not None:
                value = self._transform_value_map(value, t.static_map)
            elif callable(t.method):
                value = self._transform_value_callable(value, t.method, t.kwargs)

        # ensure only a string value or None is returned (set to default if required)
        if value is None:
            value = metadata.default
        elif not isinstance(value, str):
            value = str(value)

        return value

    def _transform_value_callable(
        self, value: Union[dict, list, str], c: Callable, kwargs=None
    ) -> Union[Optional[str], Optional[List[str]]]:
        """Transform values in the TI data."""
        # find signature of method and call with correct args
        kwargs = kwargs or {}
        try:
            sig = signature(c, follow_wrapped=True)
            if 'ti_dict' in sig.parameters:
                kwargs.update({'ti_dict': self.ti_dict})
            if 'transform' in sig.parameters:
                kwargs.update({'transform': self})
        except ValueError:  # signature doesn't work for many built-in methods/functions
            pass

        # pass value to transform callable/method, which should always return a string
        return c(value, **kwargs)

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
            # self.log.trace('feature=transform, action=transform-values, metadata=None')
            return []

        # not all metadata fields have a path, but they must have a path or default
        if metadata.path is None:
            default = _default()
            # self.log.trace(
            #     f'feature=transform, action=transform-values, metadata-path=None, value={default}'
            # )
            return default

        # path search can return multiple data types and single or multiple values
        value = self._path_search(metadata.path)

        # return default if value of None is returned from Path
        # IMPORTANT: a None value passed to the transform may cause a failure (lambda x: x.lower())
        if value in [None, []]:
            default = _default()
            # self.log.trace(
            #     f'feature=transform, action=transform-values, metadata-path=None, value={default}'
            # )
            return default

        for t in metadata.transform or []:
            if t.filter_map is not None:
                # when path search returns an array of values, each value is mapped
                value = [
                    self._transform_value_map(v, t.filter_map, True)
                    for v in self._always_array(value)
                ]
            elif t.static_map is not None:
                # when path search returns an array of values, each value is mapped
                _values = []
                for v in self._always_array(value):
                    v = self._transform_value_map(v, t.static_map)
                    if v is not None:
                        _values.append(v)
                value = _values
            elif callable(t.method):
                value = self._transform_value_callable(value, t.method, t.kwargs)
            elif callable(t.for_each):
                value = [
                    self._transform_value_callable(v, t.for_each, t.kwargs) if v is not None else v
                    for v in self._always_array(value)
                ]

        # the output should be an array of strings or empty array
        _value = []
        for v in self._always_array(value):
            if v in [None, '']:
                if metadata.default is not None:
                    _value.append(metadata.default)
                else:
                    _value.append(v)
            else:
                _value.append(v)

        # self.log.trace(f'feature=transform, action=transform-values, value={_value}')
        return _value

    def _validate_transforms(self):
        """Validate the transform model."""
        if len(self.transforms) > 1:
            for transform in self.transforms:
                if transform.applies is None:
                    raise ValidationError(
                        'If more than one transform is provided, each '
                        'provided transform must provide an apply field.',
                        None,
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
    def add_file_occurrence(
        self,
        file_name: Optional[str] = None,
        path: Optional[str] = None,
        date: Optional[datetime] = None,
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
