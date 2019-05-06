# -*- coding: utf-8 -*-
"""ThreatConnect TI Email """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Email(Group):
    """Unique API calls for Email API Endpoints"""

    def __init__(self, tcex, name, to, from_addr, subject, body, header, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            subject (str): The subject for this Email.
            header (str): The header for this Email.
            body (str): The body for this Email.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            from_addr (str, kwargs): The **from** address for this Email.
            to (str, kwargs): The **to** address for this Email.
        """
        super(Email, self).__init__(tcex, 'Email', 'email', 'emails', name, owner, **kwargs)
        self._data['to'] = to or kwargs.get('to')
        self._data['from'] = from_addr or kwargs.get('from_addr')
        self._data['subject'] = subject or kwargs.get('subject')
        self._data['body'] = body or kwargs.get('body')
        self._data['header'] = header or kwargs.get('header')
        self._data['score'] = kwargs.get('score', 0)
