# -*- coding: utf-8 -*-
"""ThreatConnect TI File"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class File(Indicator):
    """Unique API calls for File API Endpoints"""

    def __init__(self, tcex, md5=None, sha1=None, sha256=None, **kwargs):
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
            xid (str, kwargs): The external id for this Indicator.
        """
        super(File, self).__init__(tcex, 'files', **kwargs)
        self.api_entity = 'file'
        if md5:
            self.data['md5'] = md5
        if sha1:
            self.data['sha1'] = sha1
        if sha256:
            self.data['sha256'] = sha256
        if 'size' not in self.data:
            self.data['size'] = 0

    def can_create(self):
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get('md5') or self.data.get('sha1') or self.data.get('sha256'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """

        :param json_response:
        """
        self.unique_id = (
            json_response.get('md5')
            or json_response.get('sha1')
            or json_response.get('sha256')
            or ''
        )

    @staticmethod
    def build_summary(val1=None, val2=None, val3=None):
        """Build the Indicator summary using available values."""
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

    # def action(self, relationship):
    #     """Add a File Action."""
    #     action_obj = FileAction(self._data.get('xid'), relationship)
    #     self._file_actions.append(action_obj)
    #     return action_obj


# class FileAction(object):
#     """ThreatConnect Batch FileAction Object"""
#
#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = ['_action_data', '_children', 'xid']
#
#     def __init__(self, parent_xid, relationship):
#         """Initialize Class Properties.
#
#         .. warning:: This code is not complete and may require some update to the API.
#
#         Args:
#             parent_xid (str): The external id of the parent Indicator.
#             relationship: ???
#         """
#         self.xid = str(uuid.uuid4())
#         self._action_data = {
#             'indicatorXid': self.xid,
#             'relationship': relationship,
#             'parentIndicatorXid': parent_xid,
#         }
#         self._children = []
#
#     @property
#     def data(self):
#         """Return File Occurrence data."""
#         if self._children:
#             for child in self._children:
#                 self._action_data.setdefault('children', []).append(child.data)
#         return self._action_data
#
#     def action(self, relationship):
#         """Add a nested File Action."""
#         action_obj = FileAction(self.xid, relationship)
#         self._children.append(action_obj)
#
#     def __str__(self):
#         """Return string represtentation of object."""
#         return json.dumps(self.data, indent=4)
