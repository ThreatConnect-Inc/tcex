# -*- coding: utf-8 -*-
"""ThreatConnect TI Report"""
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Report(Group):
    """Unique API calls for Report API Endpoints"""

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_name (str, kwargs): The name for the attached file for this Group.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                                               file content.
            publish_date (str, kwargs): The publish datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super(Report, self).__init__(tcex, 'reports', name, **kwargs)
        self.api_entity = 'report'
        # file data/content to upload

    def file_content(self, file_content, update_if_exists=True):
        """Set Document or Report file data.
        :param file_content:
        :param update_if_exists:
        :return:
        """

        self._data['fileContent'] = file_content
        return self.tc_requests.upload(self.api_type, self.api_sub_type, self.unique_id,
                                       file_content, update_if_exists=update_if_exists)

    def file_name(self, file_name):
        """Return Email to.
        :param file_name:
        :return:
        """
        self._data['fileName'] = file_name
        request = {'fileName': file_name}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def file_size(self, file_size):
        """Return Email to.
        :param file_size:
        :return:
        """
        self._data['fileSize'] = file_size
        request = {'fileSize': file_size}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def status(self, status):
        """Return Email to.
        :param status:
        :return:
        """
        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

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
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def publish_date(self, publish_date):
        """Return Email to.
        :param publish_date:
        :return:
        """
        publish_date = self._utils.format_datetime(publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')

        self._data['publishDate'] = publish_date
        request = {'publishDate': publish_date}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)
