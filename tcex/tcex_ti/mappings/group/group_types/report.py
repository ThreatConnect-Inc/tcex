# -*- coding: utf-8 -*-
"""ThreatConnect TI Report"""
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Report(Group):
    """Unique API calls for Report API Endpoints"""

    def __init__(self, tcex, name, owner=None, **kwargs):
        """Initialize Class Properties.

        Valid status:
        + Success
        + Awaiting Upload
        + In Progress
        + Failed

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_name (str, kwargs): The name for the attached file for this Group.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                                               file content.
            publish_date (str, kwargs): The publish datetime expression for this Group.
        """
        super(Report, self).__init__(tcex, 'Report', 'report', 'reports', name, owner, **kwargs)

    def file_content(self, file_content, update_if_exists=True):
        """
        Updates the file content.

        Args:
            file_content: The file_content to upload.
            update_if_exists:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['fileContent'] = file_content
        return self.tc_requests.upload(
            self.api_type,
            self.api_branch,
            self.unique_id,
            file_content,
            update_if_exists=update_if_exists,
        )

    def file_name(self, file_name):
        """
        Updates the file_name.

        Args:
            file_name:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['fileName'] = file_name
        request = {'fileName': file_name}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def file_size(self, file_size):
        """
        Updates the file_size.

        Args:
            file_size:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['fileSize'] = file_size
        request = {'fileSize': file_size}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def status(self, status):
        """
        Updates the status

        Valid status:
        + Success
        + Awaiting Upload
        + In Progress
        + Failed

        Args:
            status: Success, Awaiting Upload, In Progress, or Failed
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def malware(self, malware, password, file_name):
        """
        Uploads to malware vault.

        Args:
            malware:
            password:
            file_name:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['malware'] = malware
        self._data['password'] = password
        self._data['fileName'] = file_name
        request = {'malware': malware, 'password': password, 'fileName': file_name}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def publish_date(self, publish_date):
        """Return Email to.
        :param publish_date:
        :return:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        publish_date = self._utils.format_datetime(publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')

        self._data['publishDate'] = publish_date
        request = {'publishDate': publish_date}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
