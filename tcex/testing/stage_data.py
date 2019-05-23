# -*- coding: utf-8 -*-
"""Stage Data Testing Module"""
import base64
import binascii
import sys


# pylint: disable=R0201
class StageData(object):
    """Stage Data class"""

    def __init__(self, tcex):
        """Initialize class properties"""
        self.tcex = tcex


class Redis(StageData):
    """Stages the Redis Data"""

    def from_dict(self, staging_data):
        """Stage redis data from dict"""
        for sd in staging_data:
            data = sd.get('data')
            data_type = self.tcex.playbook.variable_type(data)
            variable = sd.get('variable')

            if data_type == 'Binary':
                data = self._decode_binary(data, variable)
            elif data_type == 'BinaryArray':
                data = [self._decode_binary(d, variable) for d in data]
                # decoded_data = []
                # for d in data:
                #     decoded_data.append(self._decode_binary(d, variable))
                # data = decoded_data
            self.tcex.playbook.create(variable, data)

    def stage(self, variable, data):
        """Stage data in redis"""
        self.tcex.playbook.create(variable, data)

    @staticmethod
    def _decode_binary(binary_data, variable):
        """Base64 decode binary data."""
        try:
            data = base64.b64decode(binary_data)
        except binascii.Error:
            print(
                'The Binary staging data for variable {} is not properly base64 '
                'encoded.'.format(variable)
            )
            sys.exit()
        return data


class ThreatConnect(StageData):
    """Stages the ThreatConnect Data"""

    def stage_tc(self, entity, owner, batch=False):
        """Stage data in ThreatConnect"""

    def stage_tc_from_dict(self, entity, owner, batch=False):
        """Stage data in ThreatConnect from dict"""
