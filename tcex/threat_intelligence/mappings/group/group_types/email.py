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

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties."""
        super().__init__(tcex, sub_type='Email', api_entity='email', api_branch='emails', **kwargs)
