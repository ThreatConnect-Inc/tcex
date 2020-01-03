# -*- coding: utf-8 -*-
"""ThreatConnect TQL"""
from enum import Enum


class TQL:
    """ThreatConnect TQL"""

    class Operator(Enum):
        """Available TQL Operators"""

        EQ = '='
        NE = '!='
        GT = '>'
        LT = '<'
        LEQ = '<='
        GEQ = '>='
        NOT_IN = 'NOT IN'
        IN = 'IN'
        NOT_LIKE = 'NOT LIKE'
        LIKE = 'LIKE'
        NOT_CONTAINS = 'NOT CONTAINS'
        CONTAINS = 'CONTAINS'
        NOT_STARTS_WITH = 'NOT STARTSWITH'
        STARTS_WITH = 'STARTSWITH'
        NOT_ENDS_WITH = 'NOT ENDSWITH'
        ENDS_WITH = 'ENDSWITH'

        @staticmethod
        def supported():
            """Supported operation strings"""
            return [
                '=',
                '!=',
                '>',
                '<',
                '<=',
                '>=',
                'NOT IN',
                'IN',
                'NOT LIKE',
                'LIKE',
                'NOT CONTAINS',
                'CONTAINS',
                'NOT STARTSWITH',
                'STARTSWITH',
                'NOT ENDSWITH',
                'ENDSWITH',
            ]

        def get(self, operator):
            """Get Enum OBJ from string"""
            operator = operator.upper()
            operator_obj = None
            if operator == '=':
                operator_obj = self.EQ
            elif operator == '!=':
                operator_obj = self.NE
            elif operator == '>':
                operator_obj = self.GT
            elif operator == '<':
                operator_obj = self.LT
            elif operator == '<=':
                operator_obj = self.LEQ
            elif operator == '>=':
                operator_obj = self.GEQ
            elif operator == 'NOT IN':
                operator_obj = self.NOT_IN
            elif operator == 'IN':
                operator_obj = self.IN
            elif operator == 'NOT LIKE':
                operator_obj = self.NOT_LIKE
            elif operator == 'LIKE':
                operator_obj = self.LIKE
            elif operator == 'NOT CONTAINS':
                operator_obj = self.NOT_CONTAINS
            elif operator == 'CONTAINS':
                operator_obj = self.CONTAINS
            elif operator in ['NOT STARTSWITH', 'NOT STARTS WITH']:
                operator_obj = self.NOT_STARTS_WITH
            elif operator in ['STARTSWITH', 'STARTS WITH']:
                operator_obj = self.STARTS_WITH
            elif operator in ['NOT ENDSWITH', 'NOT ENDS WITH']:
                operator_obj = self.NOT_ENDS_WITH
            elif operator in ['ENDSWITH', 'ENDS WITH']:
                operator_obj = self.ENDS_WITH
            return operator_obj

    class Type(Enum):
        """Enum representing available value types"""

        STRING = 'String'
        INTEGER = 'Integer'
        BOOLEAN = 'Boolean'

    def __init__(self):
        """Initialize Class Properties"""
        self._filters = []
        self.raw_tql = None

    @property
    def as_str(self):
        """Convert the TQL obj to a string"""
        filters = []
        for tql_filter in self.filters:
            value = tql_filter.get('value')
            keyword = tql_filter.get('keyword')
            if keyword.startswith('has'):
                values = value
                if not isinstance(value, list):
                    values = [value]
                if tql_filter.get('type') == self.Type.STRING:
                    values = [f'"{value}"' for value in values]
                # value = f"({','.join(values)})"
                value = f"({','.join([str(v) for v in values])})"
            if tql_filter.get('type') == self.Type.STRING:
                value = f'"{value}"'
            filters.append(f"{tql_filter.get('keyword')} {tql_filter.get('operator').name} {value}")

        return ' and '.join(filters)

    @property
    def filters(self):
        """Return the filters"""
        return self._filters

    @filters.setter
    def filters(self, filters):
        """Set the filters"""
        self._filters = filters

    def add_filter(self, keyword, operator, value, type_=Type.STRING):
        """Add a filter to the current obj

        Args:
            keyword (str): the field to search on
            operator (str): the operator to use
            value (str): the value to compare
            type_ (Type): How to treat the value (defaults to String)
        """
        self.filters.append(
            {'keyword': keyword, 'operator': operator, 'value': value, 'type': type_}
        )

    def set_raw_tql(self, tql):
        """Set a raw TQL filter"""
        self.raw_tql = tql

    def get_operator(self, operator):
        """Get Enum OBJ from string"""
        operator = operator.upper()
        operator_obj = None
        if operator == '=':
            operator_obj = self.Operator.EQ
        elif operator == '!=':
            operator_obj = self.Operator.NE
        elif operator == '>':
            operator_obj = self.Operator.GT
        elif operator == '<':
            operator_obj = self.Operator.LT
        elif operator == '<=':
            operator_obj = self.Operator.LEQ
        elif operator == '>=':
            operator_obj = self.Operator.GEQ
        elif operator == 'NOT IN':
            operator_obj = self.Operator.NOT_IN
        elif operator == 'IN':
            operator_obj = self.Operator.IN
        elif operator == 'NOT LIKE':
            operator_obj = self.Operator.NOT_LIKE
        elif operator == 'LIKE':
            operator_obj = self.Operator.LIKE
        elif operator == 'NOT CONTAINS':
            operator_obj = self.Operator.NOT_CONTAINS
        elif operator == 'CONTAINS':
            operator_obj = self.Operator.CONTAINS
        elif operator in ['NOT STARTSWITH', 'NOT STARTS WITH']:
            operator_obj = self.Operator.NOT_STARTS_WITH
        elif operator in ['STARTSWITH', 'STARTS WITH']:
            operator_obj = self.Operator.STARTS_WITH
        elif operator in ['NOT ENDSWITH', 'NOT ENDS WITH']:
            operator_obj = self.Operator.NOT_ENDS_WITH
        elif operator in ['ENDSWITH', 'ENDS WITH']:
            operator_obj = self.Operator.ENDS_WITH
        return operator_obj
