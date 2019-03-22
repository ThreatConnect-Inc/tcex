# -*- coding: utf-8 -*-
"""ThreatConnect TI Threat"""
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Threat(Group):
    """Unique API calls for Threat API Endpoints"""

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super(Threat, self).__init__(tcex, 'threats', name, **kwargs)
        self.api_entity = 'threat'
