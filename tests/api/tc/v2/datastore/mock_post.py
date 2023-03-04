"""Test Helper"""
# standard library
import json
from typing import Any


class MockPost:
    """Mock tcex session.get() method."""

    def __init__(self, data: Any, ok=True):
        """Initialize class properties."""
        self.data = data
        self._ok = ok

    @property
    def headers(self):
        """Mock headers property"""
        return {'content-type': 'application/json'}

    def json(self):
        """Mock json method"""
        return self.data

    @property
    def ok(self):
        """Mock ok property"""
        return self._ok

    @property
    def reason(self):
        """Mock reason property"""
        return 'reason'

    @property
    def status_code(self):
        """Mock status_code property"""
        return 500

    @property
    def text(self):
        """Mock text property"""
        return json.dumps(self.data)
