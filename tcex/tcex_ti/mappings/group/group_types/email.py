from tcex.tcex_ti.mappings.group import Group


class Email(Group):
    """ThreatConnect Batch Email Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, name, subject, header, body, **kwargs):
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
        self._data['subject'] = subject
        self._data['header'] = header
        self._data['body'] = body
        self._data['score'] = kwargs.get('score', 0)

    def to(self, to):
        """Set Document first seen."""
        self._data['to'] = to
        request = {'to': to}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def from_addr(self, from_addr):
        """Return Email to."""
        self._data['from'] = from_addr
        request = {'from': from_addr}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def score(self, score):
        """Return Email to."""
        self._data['score'] = score
        request = {'score': score}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def subject(self, subject):
        """Return Email to."""
        self._data['subject'] = subject
        request = {'subject': subject}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def header(self, header):
        """Return Email to."""
        self._data['header'] = header
        request = {'header': header}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def body(self, body):
        """Return Email to."""
        self._data['body'] = body
        request = {'body': body}
        return self._tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

