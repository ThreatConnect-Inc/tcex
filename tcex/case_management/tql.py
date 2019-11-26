from enum import Enum


class TQL(object):
    class Operator(Enum):
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
            return [
                '=', '!=', '>', '<', '<=', '>=', 'NOT IN', 'IN', 'NOT LIKE', 'LIKE', 'NOT CONTAINS',
                'CONTAINS', 'NOT STARTSWITH', 'STARTSWITH', 'NOT ENDSWITH', 'ENDSWITH',
            ]

        def get(self, operator):
            operator = operator.upper()
            if operator == '=':
                return self.EQ
            elif operator == '!=':
                return self.NE
            elif operator == '>':
                return self.GT
            elif operator == '<':
                return self.LT
            elif operator == '<=':
                return self.LEQ
            elif operator == '>=':
                return self.GEQ
            elif operator == 'NOT IN':
                return self.NOT_IN
            elif operator == 'IN':
                return self.IN
            elif operator == 'NOT LIKE':
                return self.NOT_LIKE
            elif operator == 'LIKE':
                return self.LIKE
            elif operator == 'NOT CONTAINS':
                return self.NOT_CONTAINS
            elif operator == 'CONTAINS':
                return self.CONTAINS
            elif operator == 'NOT STARTSWITH' or operator == 'STARTS WITH':
                return self.NOT_STARTS_WITH
            elif operator == 'STARTSWITH' or operator == 'STARTS WITH':
                return self.STARTS_WITH
            elif operator == 'NOT ENDSWITH' or operator == 'NOT ENDS WITH':
                return self.NOT_ENDS_WITH
            elif operator == 'ENDSWITH' or operator == 'ENDS WITH':
                return self.ENDS_WITH
            else:
                return None

    class Type(Enum):
        STRING = 'String'
        INTEGER = 'Integer'
        BOOLEAN = 'Boolean'

    def __init__(self):
        self._filters = []
        self.raw_tql = None

    @property
    def as_str(self):
        filters = []
        for filter in self.filters:
            value = filter.get('value')
            keyword = filter.get('keyword')
            if keyword.startswith('has'):
                values = value
                if not isinstance(value, list):
                    values = [value]
                if filter.get('type') == self.Type.STRING:
                    values = ['"{0}"'.format(value) for value in values]
                value = '({})'.format(','.join(values))
            if filter.get('type') == self.Type.STRING:
                value = '"{}"'.format(value)
            filters.append('{} {} {}'.format(
                filter.get('keyword'), filter.get('operator').name, value
            ))

        return ' and '.join(filters)

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, filters):
        self._filters = filters

    def add_filter(self, keyword, operator, value, type=Type.STRING):
        self.filters.append(
            {'keyword': keyword, 'operator': operator, 'value': value, 'type': type}
        )

    def set_raw_tql(self, tql):
        self.raw_tql = tql

    def get_operator(self, operator):
        operator = operator.upper()
        if operator == '=':
            return self.Operator.EQ
        elif operator == '!=':
            return self.Operator.NE
        elif operator == '>':
            return self.Operator.GT
        elif operator == '<':
            return self.Operator.LT
        elif operator == '<=':
            return self.Operator.LEQ
        elif operator == '>=':
            return self.Operator.GEQ
        elif operator == 'NOT IN':
            return self.Operator.NOT_IN
        elif operator == 'IN':
            return self.Operator.IN
        elif operator == 'NOT LIKE':
            return self.Operator.NOT_LIKE
        elif operator == 'LIKE':
            return self.Operator.LIKE
        elif operator == 'NOT CONTAINS':
            return self.Operator.NOT_CONTAINS
        elif operator == 'CONTAINS':
            return self.Operator.CONTAINS
        elif operator == 'NOT STARTSWITH' or operator == 'STARTS WITH':
            return self.Operator.NOT_STARTS_WITH
        elif operator == 'STARTSWITH' or operator == 'STARTS WITH':
            return self.Operator.STARTS_WITH
        elif operator == 'NOT ENDSWITH' or operator == 'NOT ENDS WITH':
            return self.Operator.NOT_ENDS_WITH
        elif operator == 'ENDSWITH' or operator == 'ENDS WITH':
            return self.Operator.ENDS_WITH
        else:
            return None
