# -*- coding: utf-8 -*-
"""ThreatConnect TI File"""
from ..indicator import Indicator


class File(Indicator):
    """Unique API calls for File API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties.

        Args:
            md5 (str, optional): The md5 value for this Indicator.
            sha1 (str, optional): The sha1 value for this Indicator.
            sha256 (str, optional): The sha256 value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            last_modified (str, kwargs): [Read-Only] The date timestamp the Indicator was last
                modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            size (str, kwargs): The file size for this Indicator.
        """
        super().__init__(tcex, sub_type='File', api_entity='file', api_branch='files', **kwargs)

        self.unique_id = (
            kwargs.get('unique_id')
            or kwargs.get('md5', None)
            or kwargs.get('sha1', None)
            or kwargs.get('sha256', None)
        )
        if self.unique_id:
            self.data['md5'] = self._hash_from_unique_id(hash_type='md5')
            self.data['sha1'] = self._hash_from_unique_id(hash_type='sha1')
            self.data['sha256'] = self._hash_from_unique_id(hash_type='sha256')
        if 'size' not in self.data:
            self.data['size'] = 0

    def _hash_from_unique_id(self, hash_type='md5'):
        if not self.unique_id:
            return None

        for hash_value in self.unique_id.split(':'):
            if hash_type.lower() == 'md5' and len(hash_value) == 32:
                return hash_value
            if hash_type.lower() == 'sha1' and len(hash_value) == 40:
                return hash_value
            if hash_type.lower() == 'sha256' and len(hash_value) == 64:
                return hash_value
        return None

    def can_create(self):
        """Return True if file can be create.

        If the md5/sha1/sha256 has been provided returns that the File can be
        created, otherwise returns that the File cannot be created.
        """
        if (
            self.unique_id
            or self.data.get('md5')
            or self.data.get('sha1')
            or self.data.get('sha256')
        ):
            return True
        return False

    def _set_unique_id(self, json_response):
        """Set the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = (
            json_response.get('md5') or json_response.get('sha1') or json_response.get('sha256')
        )

    @staticmethod
    def build_summary(val1=None, val2=None, val3=None):
        """Construct the summary given a md5, sha1, and sha256

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
        """Yield all occurrences that file has."""
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        yield from self.tc_requests.file_occurrences(
            self.api_type, self.api_branch, self.unique_id, self.owner
        )

    def get_occurrence(self, occurrence_id):
        """Return a file occurrence given an occurrence id

        Args:
            occurrence_id:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.occurrence(occurrence_id)

    def occurrence(self, occurrence_id):
        """Get a file occurrence given a occurrence id

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
        """Add  a occurrence to the file

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
        """Delete a file occurrence given a occurrence id

        Args:
            occurrence_id:

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.delete_file_occurrence(
            self.api_type, self.api_branch, self.unique_id, occurrence_id, self.owner
        )
