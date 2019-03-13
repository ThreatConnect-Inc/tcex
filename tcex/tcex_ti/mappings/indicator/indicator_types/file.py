import json
import uuid

from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class File(Indicator):
    """ThreatConnect Batch File Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

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
        summary = self.build_summary(md5, sha1, sha256)  # build the indicator summary
        super(File, self).__init__(tcex, 'files', summary, **kwargs)
        if md5:
            self._data['md5'] = md5
        if sha1:
            self._data['sha1'] = sha1
        if sha256:
            self._data['sha256'] = sha256
        if 'size' not in self._data:
            self._data['size'] = '0'

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

    def action(self, relationship):
        """Add a File Action."""
        action_obj = FileAction(self._data.get('xid'), relationship)
        self._file_actions.append(action_obj)
        return action_obj

    @property
    def md5(self):
        """Return Indicator md5."""
        return self._data.get('md5')

    @md5.setter
    def md5(self, md5):
        """Set Indicator md5."""
        self._data['md5'] = md5

    @property
    def sha1(self):
        """Return Indicator sha1."""
        return self._data.get('sha1')

    @sha1.setter
    def sha1(self, sha1):
        """Set Indicator sha1."""
        self._data['sha1'] = sha1

    @property
    def sha256(self):
        """Return Indicator sha256."""
        return self._data.get('sha256')

    @sha256.setter
    def sha256(self, sha256):
        """Set Indicator sha256."""
        self._data['sha256'] = sha256

    @property
    def size(self):
        """Return Indicator size."""
        return self._data.get('intValue1')

    @size.setter
    def size(self, size):
        """Set Indicator size."""
        self._data['intValue1'] = size


class FileAction(object):
    """ThreatConnect Batch FileAction Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = ['_action_data', '_children', 'xid']

    def __init__(self, parent_xid, relationship):
        """Initialize Class Properties.

        .. warning:: This code is not complete and may require some update to the API.

        Args:
            parent_xid (str): The external id of the parent Indicator.
            relationship: ???
        """
        self.xid = str(uuid.uuid4())
        self._action_data = {
            'indicatorXid': self.xid,
            'relationship': relationship,
            'parentIndicatorXid': parent_xid,
        }
        self._children = []

    @property
    def data(self):
        """Return File Occurrence data."""
        if self._children:
            for child in self._children:
                self._action_data.setdefault('children', []).append(child.data)
        return self._action_data

    def action(self, relationship):
        """Add a nested File Action."""
        action_obj = FileAction(self.xid, relationship)
        self._children.append(action_obj)

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)
