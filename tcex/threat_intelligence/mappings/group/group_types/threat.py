# -*- coding: utf-8 -*-
"""ThreatConnect TI Threat"""
from ..group import Group


class Threat(Group):
    """Unique API calls for Threat API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties.

        Args:
            tcex (TcEx): An instantiated instance of TcEx object.
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
        """
        super().__init__(
            tcex, sub_type='Threat', api_entity='threat', api_branch='threats', **kwargs
        )
