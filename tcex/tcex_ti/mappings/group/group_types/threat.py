# -*- coding: utf-8 -*-
"""ThreatConnect TI Threat"""
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Threat(Group):
    """Unique API calls for Threat API Endpoints"""

    def __init__(self, tcex, name, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
        """
        super(Threat, self).__init__(tcex, 'Threat', 'threat', 'threats', name, owner, **kwargs)
