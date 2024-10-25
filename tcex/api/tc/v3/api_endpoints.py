"""TcEx Framework Module"""

# standard library
from enum import Enum


class ApiEndpoints(Enum):
    """Available API Endpoints"""

    ARTIFACT_TYPES = '/v3/artifactTypes'
    ATTRIBUTE_TYPES = '/v3/attributeTypes'
    ARTIFACTS = '/v3/artifacts'
    CASES = '/v3/cases'
    CASE_ATTRIBUTES = '/v3/caseAttributes'
    GROUP_ATTRIBUTES = '/v3/groupAttributes'
    GROUPS = '/v3/groups'
    INDICATOR_ATTRIBUTES = '/v3/indicatorAttributes'
    INTEL_REQUIREMENTS = '/v3/intelRequirements'
    CATEGORIES = '/v3/intelRequirements/categories'
    RESULTS = '/v3/intelRequirements/results'
    SUBTYPES = '/v3/intelRequirements/subtypes'
    INDICATORS = '/v3/indicators'
    NOTES = '/v3/notes'
    OWNERS = '/v3/security/owners'
    OWNER_ROLES = '/v3/security/ownerRoles'
    SECURITY_LABELS = '/v3/securityLabels'
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
