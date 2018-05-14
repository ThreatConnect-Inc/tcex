# -*- coding: utf-8 -*-
""" Data Filter Module """
from builtins import int, str
import operator


class DataFilter(object):
    """Filter Single Level List of Dictionaries (JSON Object)"""

    def __init__(self, tcex, data):
        """Initialize default class values.

        .. Note:: The method only supports one level of nesting in the provided data.

        Args:
            tcex (obj): Instance of TcEx.
            data (list): List of Dictionary.
        """
        self._data = data
        # self._filtered_results = ()  # the filtered results
        self._indexes = {}
        self._master_index = {}  # bcs - is this needed?
        self._tcex = tcex

        # build the indexes
        self._build_indexes()

    def _build_indexes(self):
        """Build indexes from data for fast filtering of data.

        Building indexes of data when possible.  This is only supported when dealing with a
        List of Dictionaries with String values.
        """
        if isinstance(self._data, list):
            for d in self._data:
                if not isinstance(d, dict):
                    err = u'Cannot build index for non Dict type.'
                    self._tcex.log.error(err)
                    raise RuntimeError(err)

                data_obj = DataObj(d)
                self._master_index.setdefault(id(data_obj), data_obj)

                for key, value in d.items():
                    # bcs - update this
                    # if not isinstance(value, (types.StringType, float, int)):
                    # TODO: This is not Python 3 ready
                    if not isinstance(value, (float, int, str)):
                        # For comparison operators the value needs to be a StringType
                        self._tcex.log.debug(u'Can only build index String Types.')
                        continue

                    self._indexes.setdefault(key, {}).setdefault(value, []).append(data_obj)
        else:
            err = u'Only *List* data type is currently supported'
            self._tcex.log.error(err)
            raise RuntimeError(err)

    @staticmethod
    def _in(field, filter_value):
        """Validate field **IN** string or list.

        Args:
            filter_value (string | list): A string or list of values.

        Returns:
            (boolean): Results of check
        """
        valid = False
        if field in filter_value:
            valid = True
        return valid

    @staticmethod
    def _index_filter(index_data, filter_value, filter_operator, field_converter=None):
        """Post Filter

        Args:
            index_data (dictionary): The indexed data for the provided field.
            field (string): The field to filter on.
            filter_value (string | list): The value to match.
            filter_operator (string): The operator for comparison.
            field_converter (method): A method used to convert the field before comparison.

        Returns:
            (list): Matching data objects
        """

        filtered_data = []
        if filter_operator == operator.eq:
            if field_converter is not None:
                filter_value = field_converter(filter_value)
            # for data_obj in index_data:
            #     yield data_obj.data
            filtered_data = index_data.get(filter_value)

        else:
            for field, data_obj_list in index_data.items():
                if field_converter is not None:
                    field = field_converter(field)

                if filter_operator(field, filter_value):  # bcs enum
                    filtered_data.extend(data_obj_list)
                    # for data_obj in data_obj_list:
                    #     yield data_obj.data

        return filtered_data

    def _loop_filter(self, field, filter_value, filter_operator, field_converter=None):
        """

        Args:
            index_data (dictionary): The indexed data for the provided field.
            filter_value (string)
            filter_operator (string)
            fv_converter (method)
        """
        pass

        # if not isinstance(self._data, list):
        #     raise RuntimeError('Only *List* data type is currently supported')
        #
        # filtered_data = []
        # for d in self._data:
        #     if not isinstance(d, dict):
        #         self._tcex.log.debug(u'Can filter for non Dict type.')
        #
        #     for key, value in d.items():
        #         if field != key:
        #             continue
        #
        #         if fv_converter is not None:
        #             filter_value = fv_converter(filter_value)
        #
        #         if filter_operator(key, filter_value):
        #             filtered_data.append(value)
        #
        # return filtered_data

    @staticmethod
    def _ni(field, filter_value):
        """Validate field **NOT IN** string or list.

        Args:
            filter_value (string | list): A string or list of values.

        Returns:
            (boolean): Results of validation
        """
        valid = False
        if field not in filter_value:
            valid = True
        return valid

    @staticmethod
    def _starts_with(field, filter_value):
        """Validate field starts with provided value.

        Args:
            filter_value (string): A string or list of values.

        Returns:
            (boolean): Results of validation
        """
        valid = False
        if field.startswith(filter_value):
            valid = True
        return valid

    def filter_data(self, field, filter_value, filter_operator, field_converter=None):
        """Filter the data given the provided.

        Args:
            field (string): The field to filter on.
            filter_value (string | list): The value to match.
            filter_operator (string): The operator for comparison.
            field_converter (method): A method used to convert the field before comparison.

        Returns:
            (set): List of matching data objects
        """
        data = []
        if self._indexes.get(field) is not None:
            data = self._index_filter(
                self._indexes.get(field), filter_value, filter_operator, field_converter)
        # else:
        #     data = self._loop_filter(field, filter_value, filter_operator)

        # if set_operator == "intersection":
        #     self._filtered_results.intersection(data)
        # elif set_operator == "union":
        #     self._filtered_results.union(data)
        return set(data)

    # @property
    # def filtered_results(self):
    #     """
    #     """
    #     return self._filtered_results

    # def intersection(self, results1, results2):
    #     """Perform Intersection on the data sets.
    #
    #     Args:
    #         results1 (set): First set of objects
    #         results2 (set): Second set of objects
    #
    #     Returns:
    #         (set): List of intersected objects
    #     """
    #     return results1.intersection(results2)

    @property
    def operator(self):
        """Supported Filter Operators

        + EQ - Equal To
        + NE - Not Equal To
        + GT - Greater Than
        + GE - Greater Than or Equal To
        + LT - Less Than
        + LE - Less Than or Equal To
        + SW - Starts With
        + IN - In String or Array
        + NI - Not in String or Array
        """

        return {
            'EQ': operator.eq,
            'NE': operator.ne,
            'GT': operator.gt,
            'GE': operator.ge,
            'LT': operator.lt,
            'LE': operator.le,
            'SW': self._starts_with,
            'IN': self._in,
            'NI': self._ni  # not in
        }

    @staticmethod
    def results(data):
        """Results"""
        cdata = []
        for r in data:
            cdata.append(r.data)
        return cdata

        # def union(self, results1, results2):
        #     """Perform Union on the data sets.
        #
        #     Args:
        #         results1 (set): First set of objects
        #         results2 (set): Second set of objects
        #
        #     Returns:
        #         (set): List of intersected objects
        #     """
        #
        #     return results1.union(results2)


class DataObj(object):
    """Data Object"""

    def __init__(self, data):
        """Init Data Object"""
        self._data = data

    @property
    def data(self):
        """The data value"""
        return self._data

    def __str__(self):
        """The data as a string"""
        return self._data
