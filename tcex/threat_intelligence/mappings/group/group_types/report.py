# -*- coding: utf-8 -*-
"""ThreatConnect TI Report"""
from ..group import Group


class Report(Group):
    """Unique API calls for Report API Endpoints

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        name (str): The name for this Group.
        file_name (str, kwargs): The name for the attached file for this Group.
        publish_date (str, kwargs): The publish datetime expression for this Group.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties."""

        super().__init__(
            tcex, sub_type='Report', api_entity='report', api_branch='reports', **kwargs
        )

    def file_content(self, file_content, update_if_exists=True):
        """Update  the file content.

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
        """Update the file_name.

        Args:
            file_name:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['fileName'] = file_name
        request = {'fileName': file_name}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def file_size(self, file_size):
        """Update the file_size.

        Args:
            file_size:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['fileSize'] = file_size
        request = {'fileSize': file_size, 'fileName': self._data['fileName']}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def get_file_hash(self, hash_type='sha256'):
        """
        Getting the hash value of attached document
        Args:
            hash_type:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.get_file_hash(
            self.api_type, self.api_branch, self.unique_id, hash_type=hash_type
        )

    def status(self, status):
        """Update the status

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
        request = {'status': status, 'fileName': self._data['fileName']}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def publish_date(self, publish_date):
        """Return Email to."""
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        publish_date = self._utils.datetime.format_datetime(
            publish_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

        self._data['publishDate'] = publish_date
        request = {'publishDate': publish_date, 'fileName': self._data['fileName']}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def download(self):
        """Download the documents context.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.download(self.api_type, self.api_branch, self.unique_id)
