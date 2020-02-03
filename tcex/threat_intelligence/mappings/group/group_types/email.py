# -*- coding: utf-8 -*-
"""ThreatConnect TI Email"""
from ..group import Group


class Email(Group):
    """Unique API calls for Email API Endpoints

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        body (str): The body for this Email.
        from_addr (str, kwargs): The **from** address for this Email.
        header (str): The header for this Email.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
        subject (str): The subject for this Email.
        to (str, kwargs): The **to** address for this Email.
    """

    def __init__(self, tcex, to, **kwargs):
        """Initialize Class properties."""
        super().__init__(tcex, 'Email', 'email', 'emails', **kwargs)
        self._data['to'] = kwargs.get('to') or kwargs.get('to_addr')
        self._data['from'] = kwargs.get('from_addr') or kwargs.get('from')
        self._data['subject'] = kwargs.get('subject')
        self._data['body'] = kwargs.get('body')
        self._data['header'] = kwargs.get('header')
        self._data['score'] = kwargs.get('score', 0)
