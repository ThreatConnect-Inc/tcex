# -*- coding: utf-8 -*-
"""ThreatConnect TI Document"""
from ..group import Group


class Document(Group):
    """Unique API calls for Document API Endpoints

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
        file_name (str, kwargs): The name for the attached file for this Group.
        malware (bool, kwargs): If true the file is considered malware.
        password (str, kwargs): If malware is true a password for the zip archive is required.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties."""
        super().__init__(
            tcex, sub_type='Document', api_entity='document', api_branch='documents', **kwargs
        )

    def download(self):
        """Download the documents context.

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.download(self.api_type, self.api_branch, self.unique_id)

    def file_content(self, file_content, update_if_exists=True):
        """Update the file content.

        Args:
            file_content (bytes|str): The contents of the file to upload.
            update_if_exists (bool): If True the request will indicate to the API
                that the file should be updated if it exists.

        Returns:
            requests.Response
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
        """Update the Document file name.

        Args:
            file_name (str): The filename of the document.

        Returns:
            requests.Response
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        # update data dict with new value
        self._data['fileName'] = file_name

        # build body for PUT
        request = {'fileName': file_name}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def file_size(self, file_size):
        """Set or Update the Document file size.

        Args:
            file_name (str): The filename of the document.

        Returns:
            requests.Response
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        # update data dict with new value
        self._data['fileSize'] = file_size

        # build body for PUT
        request = {'fileName': self._data.get('fileName'), 'fileSize': file_size}
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

    def malware(self, malware, password, file_name):
        """Update the Document file to be marked as malware.

        Args:
            malware (bool): True if the document is malware.
            password (str): The password for the zip file.
            file_name (str): The filename of the document.

        Returns:
            requests.Response
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        # update data dict with new value
        self._data['malware'] = malware
        self._data['password'] = password
        self._data['fileName'] = file_name

        # build body for PUT
        request = {'fileName': file_name, 'malware': malware, 'password': password}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
