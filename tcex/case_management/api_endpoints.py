# -*- coding: utf-8 -*-
"""Case Management API Endpoints"""
# standard library
from enum import Enum, unique


@unique
class ApiEndpoints(Enum):
    """Available API Endpoints for Case Management"""

    ARTIFACT_TYPES = '/v3/artifactTypes'
    ARTIFACTS = '/v3/artifacts'
    CASES = '/v3/cases'
    NOTES = '/v3/notes'
    TAGS = '/v3/tags'
    TASKS = '/v3/tasks'
    WORKFLOW_EVENTS = '/v3/workflowEvents'
    WORKFLOW_TEMPLATES = '/v3/workflowTemplates'
