# -*- coding: utf-8 -*-
"""ThreatConnect TI Email"""
from ..group import Group


class Email(Group):
    """Unique API calls for Email API Endpoints

    Args:
        name (str): The name for this Group.
        to (str, kwargs): The **to** address for this Email.
        from_addr (str, kwargs): The **from** address for this Email.
        subject (str): The subject for this Email.
        body (str): The body for this Email.
        header (str): The header for this Email.
        owner (str): The name for this Group.
    """

    def __init__(self, tcex, name, to, from_addr, subject, body, header, owner=None, **kwargs):
        """Initialize Class properties."""
        super().__init__(tcex, 'Email', 'email', 'emails', owner=owner, name=name, **kwargs)
        self._data['to'] = to or kwargs.get('to') or kwargs.get('to_addr')
        self._data['from'] = from_addr or kwargs.get('from_addr') or kwargs.get('from')
        self._data['subject'] = subject or kwargs.get('subject')
        self._data['body'] = body or kwargs.get('body')
        self._data['header'] = header or kwargs.get('header')
        self._data['score'] = kwargs.get('score', 0)
