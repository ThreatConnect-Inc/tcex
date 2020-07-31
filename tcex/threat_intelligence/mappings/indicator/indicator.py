# -*- coding: utf-8 -*-
"""ThreatConnect TI Indicator"""
# standard library
import json
from urllib.parse import quote, unquote

from ..mappings import Mappings

# import local modules for dynamic reference
module = __import__(__name__)


def custom_indicator_class_factory(
    indicator_type, entity_type, branch_type, base_class, value_fields
):
    """Build dynamic Custom Indicator Class."""

    @staticmethod
    def _metadata_map_1():
        """Map field data."""
        metadata_map = base_class._metadata_map()
        for value in value_fields:
            manipulated_value = value.lower().replace(' ', '_')
            if manipulated_value not in metadata_map.keys():
                metadata_map[manipulated_value] = value
        return metadata_map

    def init(self, tcex, **kwargs):  # pylint: disable=possibly-unused-variable
        """Init method for Custom Indicator Types with one value"""
        base_class.__init__(
            self,
            tcex,
            sub_type=indicator_type,
            api_entity=entity_type,
            api_branch=branch_type,
            **kwargs,
        )
        res = {v: k for k, v in self._metadata_map().items()}
        values = []
        for field in value_fields:
            value = kwargs.pop(res.get(field), kwargs.pop(field, ''))
            value = quote(self.fully_decode_uri(value), safe='')
            values.append(value)

        if len(values) == 1:
            self.unique_id = kwargs.get('unique_id', values[0])
        elif len(values) == 2:
            self.unique_id = kwargs.get('unique_id', self.build_summary(values[0], values[1]))
        elif len(values) == 3:
            self.unique_id = kwargs.get(
                'unique_id', self.build_summary(values[0], values[1], values[2])
            )

    def _set_unique_id(self, json_request):
        """Set the unique ID.

        Args:
            json_request (dict): The JSON data for the request.
        """
        values = []
        for field in value_fields:
            value = json_request.get(field, '')
            values.append(quote(self.fully_decode_uri(value), safe=''))
        if len(values) == 1:
            self.unique_id = values[0]
        elif len(values) == 2:
            self.unique_id = self.build_summary(values[0], values[1])
        elif len(values) == 1:
            self.unique_id = self.build_summary(values[0], values[1], values[2])

    def can_create(self):  # pylint: disable=unused-argument,possibly-unused-variable
        """Determine if the required data that the API endpoint is expecting is present."""
        valid_create = True
        for field in value_fields:
            if not field:
                valid_create = False
        return valid_create

    class_name = indicator_type.replace(' ', '')
    init_method = locals()['init']
    set_unique_id_method = locals()['_set_unique_id']
    can_create_method = locals()['can_create']
    _metadata_map = locals()['_metadata_map_1']
    new_class = type(
        str(class_name),
        (base_class,),
        {
            '__init__': init_method,
            '_set_unique_id': set_unique_id_method,
            'can_create': can_create_method,
            '_metadata_map': _metadata_map,
        },
    )
    return new_class


class Indicator(Mappings):
    """Unique API calls for Indicator API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties."""
        super().__init__(
            tcex,
            'Indicator',
            'indicators',
            kwargs.pop('sub_type', None),
            kwargs.pop('api_entity', 'indicator'),
            kwargs.pop('api_branch', None),
            kwargs.pop('owner', None),
        )

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @property
    def as_entity(self):
        """Return the entity representation of the Indicator."""
        return {
            'type': self.api_sub_type,
            'value': unquote(self.unique_id),
            'id': self._data.get('id'),
        }

    @staticmethod
    def is_indicator():
        """Return true if object type is an indicator."""
        return True

    @property
    def owner(self):
        """Return the owner."""
        return self._owner

    def can_create(self):
        """Overridden by other indicator classes."""
        return True

    @staticmethod
    def _metadata_map():
        """Map snake case fields to camel case fields."""
        return {
            'date_added': 'dateAdded',
            'dns_active': 'dnsActive',
            'last_modified': 'lastModified',
            'private_flag': 'privateFlag',
            'whois_active': 'whoisActive',
            'key_name': 'Key Name',
            'value_type': 'Value Type',
            'value_name': 'Value Name',
            'block': 'Block',
            'mutex': 'Mutex',
            'as_number': 'AS Number',
            'hostname': 'hostName',
        }

    def add_key_value(self, key, value):
        """Convert the value and adds it as a data field.

        Args:
            key:
            value:
        """
        key = self._metadata_map().get(key, key)
        if key in ['dateAdded', 'lastModified']:
            self._data[key] = self._utils.datetime.format_datetime(
                value, date_format='%Y-%m-%dT%H:%M:%SZ'
            )
        elif key == 'confidence':
            self._data[key] = int(value)
        elif key == 'rating':
            self._data[key] = float(value)
        elif key == 'unique_id':
            self._unique_id = quote(self.fully_decode_uri(value), safe='')
        else:
            self._data[key] = value

    def status(self, status=None, cal_status=None):
        """Update the Indicators status

        Args:
            status:  Valid values to set to active are ['active', '2', '1' ] while
            ['inactive', '-2', '-1', 0] will set it to inactive
            cal_status:  Valid values to set to locked are ['locked', 'lock', '1' ] while
            ['unlock', 'unlocked', '0'] will set it to inactive

        Returns:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        if not status and not cal_status:
            return None
        request_data = {}
        if status:
            status = str(status)
            if status.lower() in ['active', '1']:
                request_data['active'] = 1
            elif status.lower() in ['inactive', '0']:
                request_data['active'] = 0
        if cal_status:
            cal_status = str(cal_status)
            if cal_status.lower() in ['locked', 'lock', '1']:
                request_data['activeLocked'] = 1
            elif cal_status.lower() in ['unlock', 'unlocked', '0']:
                request_data['activeLocked'] = 0
        return self.tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, request_data, owner=self.owner
        )

    def rating(self, value):
        """Update the Indicators rating

        Args:
            value:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        request_data = {'rating': value}
        return self.tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, request_data, owner=self.owner
        )

    def confidence(self, value):
        """Update the Indicators confidence

        Args:
            value:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        request_data = {'confidence': value}
        return self.tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, request_data, owner=self.owner
        )

    def owners(self):
        """Return owners"""
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.owners(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def add_observers(self, count, date_observed):
        """Add a Indicator Observation

        Args:
            count:
            date_observed:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        data = {
            'count': count,
            'dateObserved': self._utils.datetime.format_datetime(
                date_observed, date_format='%Y-%m-%dT%H:%M:%SZ'
            ),
        }

        return self.tc_requests.add_observations(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def observation_count(self):
        """Get the indicators observation count.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.observation_count(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def add_false_positive(self):
        """Add a Indicator FalsePositive."""
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.add_false_positive(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def observations(self):
        """Return indicator observation data.

        Returns:
            [type]: [description]
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.observations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def deleted(self, deleted_since=None, filters=None, params=None):
        """Return deleted indicators from TC REST API.

        Args:
            deleted_since ([type]): [description]
            filters ([type], optional): [description]. Defaults to None.
            params ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        return self.tc_requests.deleted(
            self.api_type,
            self.api_branch,
            deleted_since=deleted_since,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    @staticmethod
    def build_summary(val1=None, val2=None, val3=None):
        """Construct an indicator summary given va1, va2, val3.

        Args:
            val1 (str, optional): Indicator value. Defaults to None.
            val2 (str, optional): Indicator value. Defaults to None.
            val3 (str, optional): Indicator value. Defaults to None.

        Returns:
            str: <space><colon><space> delimeted indicator summary.
        """
        summary = []
        if val1 is not None:
            summary.append(val1)
        if val2 is not None:
            summary.append(val2)
        if val3 is not None:
            summary.append(val3)
        if not summary:
            return None
        return ' : '.join(summary)

    def __str__(self):
        """Return string representation of object"""
        return json.dumps(self._data, indent=4)
