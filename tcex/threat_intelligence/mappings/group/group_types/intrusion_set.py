# -*- coding: utf-8 -*-
"""ThreatConnect TI Intrusion Set"""
from ..group import Group


class IntrusionSet(Group):
    """Unique API calls for IntrustionSet API Endpoints

    Args:
        name (str): The name for this Group.
    """

    def __init__(self, tcex, name, owner=None, **kwargs):
        """Initialize Class Properties."""
        super().__init__(
            tcex, 'Intrusion Set', 'intrusionSet', 'intrusionSets', owner=owner, name=name, **kwargs
        )
