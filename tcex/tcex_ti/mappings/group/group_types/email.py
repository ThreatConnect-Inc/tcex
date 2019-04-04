# -*- coding: utf-8 -*-
"""ThreatConnect TI Email """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Email(Group):
    """Unique API calls for Email API Endpoints"""

    def __init__(self, tcex, name, to, from_addr, subject, body, header, **kwargs):
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
        super(Email, self).__init__(tcex, 'emails', name, **kwargs)
        self.api_entity = 'email'
        self._data['to'] = to or kwargs.get('to')
        self._data['from'] = from_addr or kwargs.get('from_addr')
        self._data['subject'] = subject or kwargs.get('subject')
        self._data['body'] = body or kwargs.get('body')
        self._data['header'] = header or kwargs.get('header')
        self._data['score'] = kwargs.get('score', 0)

    def to(self, to):
        """
        Updates emails To field
        Args:
            to:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['to'] = to
        request = {'to': to}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def from_addr(self, from_addr):
        """
        Updates emails from field
        Args:
            from_addr:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['from'] = from_addr
        request = {'from': from_addr}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def score(self, score):
        """
        Updates emails score field
        Args:
            score:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['score'] = score
        request = {'score': score}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def subject(self, subject):
        """
        Updates emails subject field
        Args:
            subject:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['subject'] = subject
        request = {'subject': subject}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def header(self, header):
        """
        Updates emails header field
        Args:
            header:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['header'] = header
        request = {'header': header}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def body(self, body):
        """
        Updates emails body field
        Args:
            body:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['body'] = body
        request = {'body': body}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)
