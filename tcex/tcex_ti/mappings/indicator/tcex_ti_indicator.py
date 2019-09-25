# -*- coding: utf-8 -*-
"""ThreatConnect TI Indicator"""
import json

try:
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote_plus  # Python

from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

# import local modules for dynamic reference
module = __import__(__name__)

# custom_class = custom_indicator_class_factory(
#     entry.get('name'),
#     entry.get('apiEntity'),
#     entry.get('apiBranch'),
#     Indicator,
#     class_data,
#     value_fields,
# )


def custom_indicator_class_factory(
    indicator_type, entity_type, branch_type, base_class, value_fields
):
    """Internal method for dynamically building Custom Indicator Class."""
    value_count = len(value_fields)

    def init_1(self, tcex, value1, owner=None, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with one value
        :param self:
        :param tcex:
        :param owner:
        :param value1:
        :param kwargs:
        """
        base_class.__init__(self, tcex, indicator_type, entity_type, branch_type, owner, **kwargs)
        res = {v: k for k, v in self._metadata_map().items()}
        value1 = value1 or kwargs.pop(res.get(value_fields[0]), value_fields[0])
        self._data[value_fields[0]] = value1
        self.unique_id = kwargs.get('unique_id', value1)
        if self.unique_id:
            self.unique_id = quote_plus(self.fully_decode_uri(self.unique_id))

    def _set_unique_id_1(self, json_request):
        """

        :param self:
        :param json_request:
        """
        self.unique_id = json_request.get(value_fields[0])
        if self.unique_id:
            self.unique_id = quote_plus(self.fully_decode_uri(self.unique_id))

    def _metadata_map_1(self):
        metadata_map = base_class._metadata_map(self)
        for value in value_fields:
            manipulated_value = value.lower().replace(' ', '_')
            if manipulated_value not in metadata_map.keys():
                metadata_map[manipulated_value] = value
        return metadata_map

    def can_create_1(self):  # pylint: disable=W0641
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get(value_fields[0]):
            return True
        return False

    def init_2(self, tcex, value1, value2, owner=None, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with two values.
        :param self:
        :param tcex:
        :param value1:
        :param value2:
        :param owner:
        :param kwargs:
        """
        base_class.__init__(self, tcex, indicator_type, entity_type, branch_type, owner, **kwargs)
        res = {v: k for k, v in self._metadata_map().items()}
        value1 = value1 or kwargs.pop(res.get(value_fields[0]), value_fields[0])
        value2 = value2 or kwargs.pop(res.get(value_fields[0]), value_fields[1])
        self._data[value_fields[0]] = value1
        self._data[value_fields[1]] = value2
        if value1:
            value1 = quote_plus(self.fully_decode_uri(value1))
        if value2:
            value2 = quote_plus(self.fully_decode_uri(value2))
        self.unique_id = kwargs.get('unique_id', self.build_summary(value1, value2))

    def _set_unique_id_2(self, json_request):
        """

        :param self:
        :param json_request:
        """
        value_0 = json_request.get(value_fields[0], '')
        value_1 = json_request.get(value_fields[1], '')
        self.unique_id = self.build_summary(
            quote_plus(self.fully_decode_uri(value_0)) or None,
            quote_plus(self.fully_decode_uri(value_1)) or None,
        )

    def can_create_2(self):  # pylint: disable=W0641
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get(value_fields[0]) and self.data.get(value_fields[1]):
            return True
        return False

    def init_3(self, tcex, value1, value2, value3, owner=None, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with three values.
        :param self:
        :param tcex:
        :param value1:
        :param value2:
        :param value3:
        :param kwargs:
        """
        base_class.__init__(self, tcex, indicator_type, entity_type, branch_type, owner, **kwargs)
        res = {v: k for k, v in self._metadata_map().items()}
        value1 = value1 or kwargs.pop(res.get(value_fields[0]), value_fields[0])
        value2 = value2 or kwargs.pop(res.get(value_fields[0]), value_fields[1])
        value3 = value3 or kwargs.pop(res.get(value_fields[0]), value_fields[2])
        self._data[value_fields[0]] = value1
        self._data[value_fields[1]] = value2
        self._data[value_fields[2]] = value3
        if value1:
            value1 = quote_plus(self.fully_decode_uri(value1))
        if value2:
            value2 = quote_plus(self.fully_decode_uri(value2))
        if value3:
            value3 = quote_plus(self.fully_decode_uri(value3))
        self.unique_id = kwargs.get('unique_id', self.build_summary(value1, value2, value3))

    def _set_unique_id_3(self, json_request):
        """

        :param self:
        :param json_request:
        """
        value_0 = json_request.get(value_fields[0], '')
        value_1 = json_request.get(value_fields[1], '')
        value_2 = json_request.get(value_fields[2], '')
        self.unique_id = self.build_summary(
            quote_plus(self.fully_decode_uri(value_0)) or None,
            quote_plus(self.fully_decode_uri(value_1)) or None,
            quote_plus(self.fully_decode_uri(value_2)) or None,
        )

    def can_create_3(self):  # pylint: disable=W0641
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if (
            self.data.get(value_fields[0])
            and self.data.get(value_fields[1])
            and self.data.get(value_fields[2])
        ):
            return True
        return False

    class_name = indicator_type.replace(' ', '')
    init_method = locals()['init_{}'.format(value_count)]
    set_unique_id_method = locals()['_set_unique_id_{}'.format(value_count)]
    can_create_method = locals()['can_create_{}'.format(value_count)]
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


class Indicator(TIMappings):
    """Unique API calls for Indicator API Endpoints"""

    def __init__(self, tcex, sub_type, api_entity, api_branch, owner, **kwargs):
        super(Indicator, self).__init__(
            tcex, 'Indicator', 'indicators', sub_type, api_entity, api_branch, owner
        )

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @staticmethod
    def is_indicator():
        return True

    @property
    def owner(self):
        return self._owner

    def can_create(self):
        """
        Overridden by other indicator classes.

        Returns:

         """
        return True

    def _metadata_map(self):  # pylint: disable=R0201
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
        }

    def add_key_value(self, key, value):
        """
        Converts the value and adds it as a data field.

        Args:
            key:
            value:
        """
        key = self._metadata_map().get(key, key)
        if key in ['dateAdded', 'lastModified']:
            self._data[key] = self._utils.format_datetime(value, date_format='%Y-%m-%dT%H:%M:%SZ')
        elif key == 'confidence':
            self._data[key] = int(value)
        elif key == 'rating':
            self._data[key] = float(value)
        elif key == 'unique_id':
            self._unique_id = quote_plus(self.fully_decode_uri(value))
        else:
            self._data[key] = value

    def status(self, status=None, cal_status=None):
        """
        Updates the Indicators status
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
            if status.lower() in ['active', '2', '1']:
                request_data['active'] = 2
            elif status.lower() in ['inactive', '-2', '-1', '0']:
                request_data['active'] = -2
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
        """
        Updates the Indicators rating

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
        """
        Updates the Indicators confidence

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
        """

        :return:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.owners(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def add_observers(self, count, date_observed):
        """
        Adds a Indicator Observation

        Args:
            count:
            date_observed:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        data = {
            'count': count,
            'dateObserved': self._utils.format_datetime(
                date_observed, date_format='%Y-%m-%dT%H:%M:%SZ'
            ),
        }

        return self.tc_requests.add_observations(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def observation_count(self):
        """
        Gets the indicators observation count.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.observation_count(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def add_false_positive(self):
        """
        Adds a Indicator FalsePositive
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.add_false_positive(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def observations(self):
        """
        Gets the indicators observations.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.observations(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def deleted(self, deleted_since, filters=None, params=None):
        """
        Gets the indicators deleted.

        Args:
            params:
            filters:
            deleted_since: Date since its been deleted

        """

        return self.tc_requests.deleted(
            self.api_type,
            self.api_branch,
            deleted_since,
            owner=self.owner,
            filters=filters,
            params=params,
        )

    @staticmethod
    def build_summary(val1=None, val2=None, val3=None):
        """
        Constructs the summary given va1, va2, val3

        Args:
            val1:
            val2:
            val3:

        Returns:

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
        """Return string represtentation of object"""
        return json.dumps(self._data, indent=4)
