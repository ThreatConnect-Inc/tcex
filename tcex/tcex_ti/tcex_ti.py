# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
import hashlib
import json
import os
import re
import uuid
import inflect
from enum import Enum
p = inflect.engine()

try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3




from tcex.tcex_ti.write.tcex_ti_write import TiWrite
from tcex.tcex_ti.read.tcex_ti_read import TiRead

# import local modules for dynamic reference
module = __import__(__name__)


class TcExTi(object):
    """ThreatConnect Threat Intelligence Module"""

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            tcex (obj): An instance of TcEx object.
        """
        self.tcex = tcex

        # reader and writer instance
        self._read = TiRead(tcex)
        self._write = TiWrite(tcex)

    @property
    def write(self):
        return self._write

    @property
    def read(self):
        """Return Group type."""
        return self.read

    @staticmethod
    def generate_xid(identifier=None):
        if identifier is None:
            identifier = str(uuid.uuid4())
        elif isinstance(identifier, list):
            identifier = '-'.join([str(i) for i in identifier])
            identifier = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
        return hashlib.sha256(identifier.encode('utf-8')).hexdigest()

    @property
    def read(self):
        """Instance of BatchSubmit"""
        return self._read

    @property
    def write(self):
        """Instance of BatchSubmit"""
        return self._write

    @property
    def file_len(self):
        """Return the number of current indicators."""
        return len(self._files)



    def __len__(self):
        """Return the number of groups and indicators."""
        return self.group_len + self.indicator_len

    def __str__(self):
        """Return string represtentation of object."""
        groups = []
        for group_data in self.groups.values():
            if isinstance(group_data, dict):
                groups.append(group_data)
            else:
                groups.append(group_data.data)
        for group_data in self.groups_shelf.values():
            if isinstance(group_data, dict):
                groups.append(group_data)
            else:
                groups.append(group_data.data)

        indicators = []
        for indicator_data in self.indicators.values():
            if isinstance(indicator_data, dict):
                indicators.append(indicator_data)
            else:
                indicators.append(indicator_data.data)
        for indicator_data in self.indicators_shelf.values():
            if isinstance(indicator_data, dict):
                indicators.append(indicator_data)
            else:
                indicators.append(indicator_data.data)

        data = {'group': groups, 'indicators': indicators}
        return json.dumps(data, indent=4, sort_keys=True)

    @read.setter
    def read(self, value):
        self._read = value

    @write.setter
    def write(self, value):
        self._write = value
