class TQL(object):
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
                values = ['"{0}"'.format(value) for value in values]
                value = '({})'.format(','.join(values))
            filters.append('{} {} "{}"'.format(
                filter.get('keyword'), filter.get('operator'), value
            ))
        return ' and '.join(filters)

    @property
    def filters(self):
        return self._filters

    @filters.setter
    def filters(self, filters):
        self._filters = filters

    def add_filter(self, keyword, operator, value):
        operator = operator.upper()
        if operator not in self.operators:
            # Log a error
            return None
        self.filters.append(
            {'keyword': keyword, 'operator': operator, 'value': value}
        )

    @property
    def operators(self):
        return [
            '=', '==', 'EQ', 'EQUALS',
            '!=', 'NE',
            '>', 'GT',
            '<', 'LT',
            '<=', 'LEQ',
            '>=', 'GEQ',
            'NOT IN', 'IN',
            'NOT LIKE', 'LIKE',
            'NOT CONTAINS', 'CONTAINS',
            'NOT STARTSWITH', 'STARTSWITH',
            'NOT ENDSWITH', 'ENDSWITH'
        ]