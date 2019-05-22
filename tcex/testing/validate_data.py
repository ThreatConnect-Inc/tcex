# -*- coding: utf-8 -*-
"""Validate Data Testing Module"""


# pylint: disable=R0201
class ValidateData(object):
    """Validate Data class"""

    def __init__(self, tcex):
        """Initialize class properties"""
        self.tcex = tcex

    def validate_redis_data(self, variable):
        """Validate Redis Data"""

    def validate_redis_eq(self, variable, data, operator):
        """Validate Redis Data"""
        # self.tcex.playbook.read(variable)
        # do the magic

    def validate_redis_gt(self, variable, data, operator):
        """Validate Redis Data"""

    def validate_redis_dd(self, variable, data, operator):
        """Compare with Deepdiff"""

    def validate_tc_from_directory(self, directory):
        """Validate ThreatConnect Threat Intelligence Data from a Directory"""

    def validate_tc(self, tcentity, file=None):
        """Validate ThreatConnect Threat Intelligence Data"""
        # parse data to find type
        # if group get xid
        # retrieve

        # do md5 on binary file
