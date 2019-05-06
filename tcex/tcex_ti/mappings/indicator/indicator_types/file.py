# -*- coding: utf-8 -*-
"""ThreatConnect TI File"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class File(Indicator):
    """Unique API calls for File API Endpoints"""

    def __init__(self, tcex, md5=None, sha1=None, sha256=None, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            md5 (str, optional): The md5 value for this Indicator.
            sha1 (str, optional): The sha1 value for this Indicator.
            sha256 (str, optional): The sha256 value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            size (str, kwargs): The file size for this Indicator.
        """
        super(File, self).__init__(tcex, 'File', 'file', 'files', owner, **kwargs)
        if md5:
            self.data['md5'] = md5
        if sha1:
            self.data['sha1'] = sha1
        if sha256:
            self.data['sha256'] = sha256
        if 'size' not in self.data:
            self.data['size'] = 0
        self.unique_id = (
            self.unique_id
            or md5
            or sha1
            or sha256
            or kwargs.get('md5', None)
            or kwargs.get('sha1', None)
            or kwargs.get('sha256', None)
        )

    def can_create(self):
        """
        If the md5/sha1/sha256 has been provided returns that the File can be
        created, otherwise returns that the File cannot be created.

        Returns:

        """
        if self.data.get('md5') or self.data.get('sha1') or self.data.get('sha256'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = (
            json_response.get('md5')
            or json_response.get('sha1')
            or json_response.get('sha256')
            or ''
        )

    @staticmethod
    def build_summary(val1=None, val2=None, val3=None):
        """
        Constructs the summary given a md5, sha1, and sha256

        Args:
            val1: md5
            val2: sha1
            val3: sha256

        Returns:

        """
        summary = []
        if val1 is not None:
            summary.append(val1)
        if val2 is not None:
            summary.append(val2)
        if val3 is not None:
            summary.append(val3)
        if not summary:
            # Indicator object has no logger to output warning
            pass
        return ' : '.join(summary)

    def occurrences(self):
        """
        Yields all occurrences that file has.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        for o in self.tc_requests.file_occurrences(
            self.api_type, self.api_branch, self.unique_id, self.owner
        ):
            yield o

    def get_occurrence(self, occurrence_id):
        """
        Gets a file occurrence given a occurrence id
        Args:
            occurrence_id:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.occurrence(occurrence_id)

    def occurrence(self, occurrence_id):
        """
        Gets a file occurrence given a occurrence id
        Args:
            occurrence_id:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.file_occurrence(
            self.api_type, self.api_branch, self.unique_id, occurrence_id, self.owner
        )

    def add_occurrence(self, name, date, path):
        """
        Adds a occurrence to the file
        Args:
            name:
            date:
            path:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.add_file_occurrence(
            self.api_type, self.api_branch, self.unique_id, name, date, path, self.owner
        )

    def delete_occurrence(self, occurrence_id):
        """
        Deletes a file occurrence given a occurrence id
        Args:
            occurrence_id:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.delete_file_occurrence(
            self.api_type, self.api_branch, self.unique_id, occurrence_id, self.owner
        )
