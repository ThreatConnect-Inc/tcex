"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import (
        ThreatIntelligence,  # CIRCULAR-IMPORT
    )


class Report(Group):
    """Unique API calls for Report API Endpoints

    Args:
        ti: An instance of the ThreatIntelligence Class.
        name (str, kwargs): The name for this Group.
        file_name (str, kwargs): The name for the attached file for this Group.
        publish_date (str, kwargs): The publish datetime expression for this Group.
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties."""

        super().__init__(ti, sub_type='Report', api_entity='report', api_branch='reports', **kwargs)

    def file_content(self, file_content: str, update_if_exists: bool = True):
        """Update the file content."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        self._data['fileContent'] = file_content
        return self.tc_requests.upload(
            self.api_type,
            self.api_branch,
            self.unique_id,
            file_content,
            update_if_exists=update_if_exists,
        )

    def file_name(self, file_name: str):
        """Update the file_name."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        self._data['fileName'] = file_name
        request = {'fileName': file_name}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def file_size(self, file_size: int):
        """Update the file_size."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        self._data['fileSize'] = file_size
        request = {'fileSize': file_size, 'fileName': self._data['fileName']}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def get_file_hash(self, hash_type: str = 'sha256'):
        """Get the hash value of attached document"""
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.get_file_hash(
            self.api_type, self.api_branch, self.unique_id, hash_type=hash_type
        )

    def status(self, status: str):
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
            self._handle_error(910, [self.type])

        self._data['status'] = status
        request = {'status': status, 'fileName': self._data['fileName']}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def publish_date(self, publish_date):
        """Return Email to."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        publish_date = self.util.any_to_datetime(publish_date).strftime('%Y-%m-%dT%H:%M:%SZ')

        self._data['publishDate'] = publish_date
        request = {'publishDate': publish_date, 'fileName': self._data['fileName']}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def download(self):
        """Download the documents context."""
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.download(self.api_type, self.api_branch, self.unique_id)
