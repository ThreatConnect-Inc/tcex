"""ThreatConnect TQL"""
# standard library
from enum import Enum


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


class Type(Enum):
    """Enum representing available value types"""

    STRING = 'String'
    INTEGER = 'Integer'
    BOOLEAN = 'Boolean'
    SUB_QUERY = 'Sub Query'


class TQL:
    """ThreatConnect TQL"""

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
            try:
                filters.append(f"{tql_filter.get('keyword')}({value._tql.as_str})")
            except:
                if tql_filter.get('type') == Type.STRING:
                    value = f'"{value}"'
                filters.append(
                    f"{tql_filter.get('keyword')} {tql_filter.get('operator').name} {value}"
                )

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
