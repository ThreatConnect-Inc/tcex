# -*- coding: utf-8 -*-
"""ThreatConnect TI Document """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Document(Group):
    """Unique API calls for Document API Endpoints"""

    def __init__(self, tcex, name, file_name, file_content, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached file for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                                               file content.
            malware (bool, kwargs): If true the file is considered malware.
            password (bool, kwargs): If malware is true a password for the zip archive is required.
            xid (str, kwargs): The external id for this Group.
        """
        super(Document, self).__init__(tcex, 'documents', name, **kwargs)
        self._data['fileName'] = file_name or kwargs.get('file_name')
        self._data['fileContent'] = file_content or kwargs.get('file_content')
        self.api_entity = 'document'
        # file data/content to upload

    def file_content(self, file_content, update_if_exists=True):
        """Set Document or Report file data.
        :param file_content:
        :param update_if_exists:
        :return:
        """

        self._data['fileContent'] = file_content
        request = {'fileContent': file_content, 'update_if_exists': update_if_exists}
        return self.tc_requests.upload(self.api_type, self.api_sub_type, self.unique_id, request)

    def file_name(self, file_name):
        """Return Email to.
        :param file_name:
        :return:
        """
        self._data['fileName'] = file_name
        request = {'fileName': file_name}
        return self.tc_requests.upload(self.api_type, self.api_sub_type, self.unique_id, request)

    def file_size(self, file_size):
        """Return Email to.
        :param file_size:
        :return:
        """
        self._data['fileSize'] = file_size
        request = {'fileSize': file_size}
        return self.tc_requests.upload(self.api_type, self.api_sub_type, self.unique_id, request)

    def status(self, status):
        """Return Email to.
        :param status:
        :return:
        """
        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.upload(self.api_type, self.api_sub_type, self.unique_id, request)

    def malware(self, malware, password, file_name):
        """

        :param malware:
        :param password:
        :param file_name:
        :return:
        """
        self._data['malware'] = malware
        self._data['password'] = password
        self._data['fileName'] = file_name
        request = {'malware': malware, 'password': password, 'fileName': file_name}
        return self.tc_requests.upload(self.api_type, self.api_sub_type, self.unique_id, request)
