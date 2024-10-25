"""TcEx Framework Module"""

# standard library
from datetime import datetime
from enum import Enum

# third-party
from arrow import Arrow

# first-party
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class Tql:
    """ThreatConnect TQL"""

    def __init__(self):
        """Initialize instance properties"""
        self._filters = []
        self.raw_tql = None

    @property
    def as_str(self):
        """Convert the TQL obj to a string"""
        filters = []
        for tql_filter in self.filters:
            # keywords are all one work (e.g. task_id should be taskid)
            keyword = tql_filter['keyword'].replace('_', '')
            value = tql_filter['value']
            try:
                filters.append(f'''{keyword}({value._tql.as_str})''')
            except Exception:
                if isinstance(value, list):
                    if tql_filter.get('type') in (TqlType.FLOAT, TqlType.INTEGER):
                        value = [str(int_) for int_ in value]
                    elif tql_filter.get('type') == TqlType.STRING:
                        value = [f'"{str(str_)}"' for str_ in value]
                    value = ','.join(value)
                    value = f'({value})'
                elif tql_filter.get('type') == TqlType.STRING:
                    value = f'"{value}"'
                filters.append(f'''{keyword} {tql_filter['operator'].value} {value}''')

        return ' and '.join(filters)

    @property
    def filters(self) -> list[dict]:
        """Return the filters"""
        return self._filters

    @filters.setter
    def filters(self, filters: list[dict]):
        """Set the filters"""
        self._filters = filters

    def add_filter(
        self,
        keyword: str,
        operator: Enum | str,
        value: int | float | list | str | FilterABC | Arrow | datetime,
        type_: TqlType | None = TqlType.STRING,
    ):
        """Add a filter to the current obj

        Args:
            keyword: the field to search on
            operator: the operator to use
            value: the value to compare
            type_: How to treat the value (defaults to String)
        """
        self.filters.append(
            {'keyword': keyword, 'operator': operator, 'value': value, 'type': type_}
        )

    def set_raw_tql(self, tql: str):
        """Set a raw TQL filter"""
        self.raw_tql = tql
