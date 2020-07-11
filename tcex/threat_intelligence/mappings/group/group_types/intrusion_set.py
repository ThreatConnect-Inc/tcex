# -*- coding: utf-8 -*-
"""ThreatConnect TI Intrusion Set"""
from ..group import Group


class IntrusionSet(Group):
    """Unique API calls for IntrustionSet API Endpoints

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties."""
        super().__init__(
            tcex,
            sub_type='Intrusion Set',
            api_entity='intrusionSet',
            api_branch='intrusionSets',
            **kwargs
        )
