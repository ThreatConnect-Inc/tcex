# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""
import json

from tcex.tcex_ti.read.mappings.tcex_ti_mappings import TIMappings

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
    def __init__(self, tcex, sub_type, owner, unique_id=None):
        super(Indicator, self).__init__(tcex, 'Indicator', sub_type, unique_id=unique_id)
        self._api_type = 'indicators'
        self._owner = owner

    @property
    def api_type(self):
        return self._api_type

    @api_type.setter
    def api_type(self, api_type):
        self._api_type = api_type

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        self._owner = owner

    def can_get(self):
        if self._unique_id and self._owner:
            return True
        return False


    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self._data, indent=4)


