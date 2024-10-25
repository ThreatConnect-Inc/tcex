"""TcEx Framework Module"""

# standard library
from enum import Enum, unique


@unique
class TqlType(Enum):
    """ThreatConnect API TQL Types"""

    BOOLEAN = 'Boolean'
    FLOAT = 'Float'
    INTEGER = 'Integer'
    STRING = 'String'
    SUB_QUERY = 'Sub Query'
