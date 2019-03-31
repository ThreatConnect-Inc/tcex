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
            to_addr (str, kwargs): The **to** address for this Email.
            xid (str, kwargs): The external id for this Group.
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
        """Set Document first seen.
        :param to:
        :return:
        """
        self._data['to'] = to
        request = {'to': to}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def from_addr(self, from_addr):
        """Return Email to.
        :param from_addr:
        :return:
        """
        self._data['from'] = from_addr
        request = {'from': from_addr}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def score(self, score):
        """Return Email to.
        :param score:
        :return:
        """
        self._data['score'] = score
        request = {'score': score}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def subject(self, subject):
        """Return Email to.
        :param subject:
        :return:
        """
        self._data['subject'] = subject
        request = {'subject': subject}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def header(self, header):
        """Return Email to.
        :param header:
        :return:
        """
        self._data['header'] = header
        request = {'header': header}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def body(self, body):
        """Return Email to.
        :param body:
        :return:
        """
        self._data['body'] = body
        request = {'body': body}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)
