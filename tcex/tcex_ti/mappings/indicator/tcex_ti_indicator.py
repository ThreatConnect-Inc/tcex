# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""
import json
try:
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote_plus  # Python

from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

# import local modules for dynamic reference
module = __import__(__name__)


def custom_indicator_class_factory(indicator_type, base_class, class_dict, value_fields):
    """Internal method for dynamically building Custom Indicator Class."""
    value_count = len(value_fields)

    def init_1(self, tcex, value1, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with one value"""
        summary = self.build_summary(value1)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, **kwargs)
        self._data[value_fields[0]] = value1
        # for k, v in class_dict.items():
        #     setattr(self, k, v)

    def init_2(self, tcex, value1, value2, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with two values."""
        summary = self.build_summary(value1, value2)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, **kwargs)
        self._data[value_fields[0]] = value1
        self._data[value_fields[1]] = value2

    def init_3(self, tcex, value1, value2, value3, **kwargs):  # pylint: disable=W0641
        """Init method for Custom Indicator Types with three values."""
        summary = self.build_summary(value1, value2, value3)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, **kwargs)
        self._data[value_fields[0]] = value1
        self._data[value_fields[1]] = value2
        self._data[value_fields[2]] = value3

    class_name = indicator_type.replace(' ', '')
    init_method = locals()['init_{}'.format(value_count)]
    new_class = type(str(class_name), (base_class,), {'__init__': init_method})
    return new_class


class Indicator(TIMappings):
    def __init__(self, tcex, sub_type, summary, **kwargs):
        super(Indicator, self).__init__(tcex, 'Indicator', 'indicators',  sub_type, **kwargs)

        self._data['summary'] = summary
        # is this needed for all indicators or just URL?

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    def can_create(self):
        if self._data.get('summary'):
            return True
        return False

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
        key = self._metadata_map.get(key, key)
        if key in ['dateAdded', 'lastModified']:
            self._data[key] = self._utils.format_datetime(
                value, date_format='%Y-%m-%dT%H:%M:%SZ'
            )
        elif key == 'confidence':
            self._data[key] = int(value)
        elif key == 'rating':
            self._data[key] = float(value)
        elif key == 'unique_id':
                self._unique_id = quote_plus(value)
        else:
            self._data[key] = value

    def rating(self, value):
        if not self.can_update():
            return
        request_data = {'rating': value}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request_data)

    def confidence(self, value):
        if not self.can_update():
            return
        request_data = {'confidence': value}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request_data)

    def owners(self):
        if not self.can_update():
            return
        return self.tc_requests.owners(self.api_type, self.api_sub_type, self.unique_id)

    def add_false_positive(self):
        if not self.can_update():
            return
        return self.tc_requests.add_false_positive(self.api_type, self.api_sub_type, self.unique_id)

    def observation_count(self):
        if not self.can_update():
            return
        return self.tc_requests.observation_count(self.api_type, self.api_sub_type, self.unique_id)

    def observations(self):
        if not self.can_update():
            return
        return self.tc_requests.observations(self.api_type, self.api_sub_type, self.unique_id)

    def add_observation(self, count, date_observed):
        if not self.can_update():
            return
        request_data = {'count': count, 'dateObserved': self._utils.format_datetime(
            date_observed, date_format='%Y-%m-%dT%H:%M:%SZ'
        )}
        return self.tc_requests.add_observations(self.api_type, self.api_sub_type, self.unique_id, request_data)

    def deleted(self, deleted_since):
        return self.tc_requests.deleted(self.api_type, self.api_sub_type, deleted_since)

    @staticmethod
    def build_summary(val1=None, val2=None, val3=None):
        """Build the Indicator summary using available values."""
        summary = []
        if val1 is not None:
            summary.append(val1)
        if val2 is not None:
            summary.append(val2)
        if val3 is not None:
            summary.append(val3)
        if not summary:
            # Indicator object has no logger to output warning
            pass
        return ' : '.join(summary)

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self._data, indent=4)


