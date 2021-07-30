"""ThreatConnect TI Email"""
from ..group import Group


class CourseOfAction(Group):
    """Unique API calls for CourseOfAction API Endpoints

    Args:
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize Class properties."""
        super().__init__(
            ti,
            sub_type='Course of Action',
            api_entity='courseOfAction',
            api_branch='coursesOfAction',
            **kwargs
        )
