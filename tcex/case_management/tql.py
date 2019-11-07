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

    class Type(Enum):
        STRING = 'String'
        INTEGER = 'Integer'
        BOOLEAN = 'Boolean'

    def __init__(self):
        self._filters = []

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
                if filter.get('type') in ['string', 'str']:
                    values = ['"{0}"'.format(value) for value in values]
                value = '({})'.format(','.join(values))
            if filter.get('type') in ['string', 'str']:
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

    def add_filter(self, keyword, operator, value, type=Operator.EQ):
        self.filters.append(
            {'keyword': keyword, 'operator': operator, 'value': value, 'type': type}
        )
