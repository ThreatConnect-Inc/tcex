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


def custom_indicator_class_factory(indicator_type, entity_type, base_class, value_fields):
    """Internal method for dynamically building Custom Indicator Class."""
    value_count = len(value_fields)

    def init_1(self, tcex, owner, value1, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with one value
        :param self:
        :param tcex:
        :param value1:
        :param kwargs:
        """
        base_class.__init__(self, tcex, owner, indicator_type, **kwargs)
        self.api_entity = entity_type
        self._data[value_fields[0]] = value1
        # for k, v in class_dict.items():
        #     setattr(self, k, v)

    def _set_unique_id_1(self, json_request):
        """

        :param self:
        :param json_request:
        """
        self.unique_id = json_request.get(value_fields[0])

    def can_create_1(self):  # pylint: disable=W0641
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get(value_fields[0]):
            return True
        return False

    def init_2(self, tcex, owner, value1, value2, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with two values.
        :param self:
        :param tcex:
        :param value1:
        :param value2:
        :param kwargs:
        """
        base_class.__init__(self, tcex, owner, indicator_type, **kwargs)
        self.api_entity = entity_type
        self._data[value_fields[0]] = value1
        self._data[value_fields[1]] = value2

    def _set_unique_id_2(self, json_request):
        """

        :param self:
        :param json_request:
        """
        self.unique_id = json_request.get(value_fields[0]) or json_request.get(value_fields[1])

    def can_create_2(self):  # pylint: disable=W0641
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get(value_fields[0]) and self.data.get(value_fields[1]):
            return True
        return False

    def init_3(self, tcex, owner, value1, value2, value3, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with three values.
        :param self:
        :param tcex:
        :param value1:
        :param value2:
        :param value3:
        :param kwargs:
        """
        base_class.__init__(self, tcex, owner, indicator_type, **kwargs)
        self.api_entity = entity_type
        self._data[value_fields[0]] = value1
        self._data[value_fields[1]] = value2
        self._data[value_fields[2]] = value3

    def _set_unique_id_3(self, json_request):
        """

        :param self:
        :param json_request:
        """
        self.unique_id = (
            json_request.get(value_fields[0])
            or json_request.get(value_fields[1])
            or json_request.get(value_fields[2])
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
    new_class = type(
        str(class_name),
        (base_class,),
        {
            '__init__': init_method,
            '_set_unique_id': set_unique_id_method,
            'can_create': can_create_method,
        },
    )
    return new_class


class Indicator(TIMappings):
    """Unique API calls for Indicator API Endpoints"""

    def __init__(self, tcex, sub_type, owner, **kwargs):
        super(Indicator, self).__init__(
            tcex, 'Indicator', 'indicators', sub_type, 'indicator', owner
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

    @property
    def _metadata_map(self):
        return {
            'date_added': 'dateAdded',
            'dnsActive': 'flag1',
            'dns_active': 'flag1',
            'last_modified': 'lastModified',
            'private_flag': 'privateFlag',
            'size': 'intValue1',
            'whoisActive': 'flag2',
            'whois_active': 'flag2',
        }

    def add_key_value(self, key, value):
        """
        Converts the value and adds it as a data field.

        Args:
            key:
            value:
        """
        key = self._metadata_map.get(key, key)
        if key in ['dateAdded', 'lastModified']:
            self._data[key] = self._utils.format_datetime(value, date_format='%Y-%m-%dT%H:%M:%SZ')
        elif key == 'confidence':
            self._data[key] = int(value)
        elif key == 'rating':
            self._data[key] = float(value)
        elif key == 'unique_id':
            self._unique_id = quote_plus(value)
        else:
            self._data[key] = value

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
            self.api_type, self.api_sub_type, self.unique_id, request_data, owner=self.owner
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
            self.api_type, self.api_sub_type, self.unique_id, request_data, owner=self.owner
        )

    def owners(self):
        """

        :return:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.owners(
            self.api_type, self.api_sub_type, self.unique_id, owner=self.owner
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
            'dataObserved': self._utils.format_datetime(
                date_observed, date_format='%Y-%m-%dT%H:%M:%SZ'
            ),
        }

        return self.tc_requests.add_observations(
            self.api_type, self.api_sub_type, self.unique_id, data, owner=self.owner
        )

    def observation_count(self):
        """
        Gets the indicators observation count.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.observation_count(
            self.api_type, self.api_sub_type, self.unique_id, owner=self.owner
        )

    def add_false_positive(self):
        """
        Adds a Indicator FalsePositive
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.add_false_positive(
            self.api_type, self.api_sub_type, self.unique_id, owner=self.owner
        )

    def observations(self):
        """
        Gets the indicators observations.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.observations(
            self.api_type, self.api_sub_type, self.unique_id, owner=self.owner
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
            self.api_sub_type,
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
