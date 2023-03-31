"""TcEx Framework Module"""
# standard library
from enum import Enum, unique


@unique
class TqlType(Enum):
    """ThreatConnect API TQL Types"""

    STRING = 'String'
    INTEGER = 'Integer'
    BOOLEAN = 'Boolean'
    SUB_QUERY = 'Sub Query'
