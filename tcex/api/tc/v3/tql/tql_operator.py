"""TcEx Framework Module"""

# standard library
from enum import Enum, unique


@unique
class TqlOperator(Enum):
    """ThreatConnect API TQL Operators"""

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
