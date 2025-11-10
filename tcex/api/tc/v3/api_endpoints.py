"""TcEx Framework Module"""

from enum import Enum


class ApiEndpoints(Enum):
    """Available API Endpoints"""

    ARTIFACT_TYPES = '/v3/artifactTypes'
    ATTRIBUTE_TYPES = '/v3/attributeTypes'
    ARTIFACTS = '/v3/artifacts'
    CASES = '/v3/cases'
    CASE_ATTRIBUTES = '/v3/caseAttributes'
    CATEGORIES = '/v3/intelRequirements/categories'
    EXCLUSION_LISTS = '/v3/security/exclusionLists'
    GROUP_ATTRIBUTES = '/v3/groupAttributes'
    GROUPS = '/v3/groups'
    INDICATOR_ATTRIBUTES = '/v3/indicatorAttributes'
    INDICATORS = '/v3/indicators'
    INTEL_REQUIREMENTS = '/v3/intelRequirements'
    NOTES = '/v3/notes'
    OWNERS = '/v3/security/owners'
    OWNER_ROLES = '/v3/security/ownerRoles'
    RESULTS = '/v3/intelRequirements/results'
    SECURITY_LABELS = '/v3/securityLabels'
    SUBTYPES = '/v3/intelRequirements/subtypes'
    SYSTEM_ROLES = '/v3/security/systemRoles'
    TAGS = '/v3/tags'
    TASKS = '/v3/tasks'
    USER_GROUPS = '/v3/security/userGroups'
    USERS = '/v3/security/users'
    VICTIMS = '/v3/victims'
    VICTIM_ASSETS = '/v3/victimAssets'
    VICTIM_ATTRIBUTES = '/v3/victimAttributes'
    WORKFLOW_EVENTS = '/v3/workflowEvents'
    WORKFLOW_TEMPLATES = '/v3/workflowTemplates'
