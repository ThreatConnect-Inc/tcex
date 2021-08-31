"""Case Management API Endpoints"""
# standard library
from enum import Enum, unique


@unique
class ApiEndpoints(Enum):
    """Available API Endpoints for Case Management"""

    INDICATORS = '/v3/indicators'
