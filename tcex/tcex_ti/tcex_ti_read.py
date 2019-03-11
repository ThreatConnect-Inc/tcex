# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3


# import local modules for dynamic reference
module = __import__(__name__)


class TiRead(object):
    def __init__(self, tcex, pagination=True, page_limit=10000):
        super('reader', tcex)
        """Initialize Class Properties.

        Args:
            tcex (obj): An instance of TcEx object.
        """
        self.tcex = tcex
        self.pagination = pagination
        self.page_limit = page_limit
        self.staged = []

    def adversary(self, adversary, owner_name, filters=None):
        if filters is None:
            filters = []
        # TODO: call to return the specific adversary
        return

    # If adversaries is null it will return all of them for that owner
    def adversaries(self, adversaries, owner_name, filters=None):
        if filters is None:
            filters = []
        # TODO: BATCH call to return the specific adversaries
        return

    @property.setter
    def pagination(self, value):
        if isinstance(value, bool):
            self.pagination = bool

    @property.setter
    def page_limit(self, value):
        if isinstance(value, int):
            self.page_limit = value
