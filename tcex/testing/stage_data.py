# -*- coding: utf-8 -*-
"""Stage Data Testing Module"""
import base64
import binascii
import sys
import os


# pylint: disable=R0201
class Stager(object):
    """Stage Data class"""

    def __init__(self, tcex):
        """Initialize class properties"""
        self.tcex = tcex
        self._redis = None
        self._threatconnect = None

    @property
    def redis(self):
        """Gets the current instance of Redis for staging data"""
        if not self._redis:
            self._redis = Redis(self)
        return self._redis

    @property
    def threatconnect(self):
        """Gets the current instance of ThreatConnect for staging data"""
        if not self._threatconnect:
            self._threatconnect = ThreatConnect(self)
        return self._threatconnect


class Redis(object):
    """Stages the Redis Data"""

    def __init__(self, provider):
        self.provider = provider
        self.batch = None

    def from_dict(self, staging_data):
        """Stage redis data from dict"""
        for sd in staging_data:
            data = sd.get('data')
            data_type = self.provider.tcex.playbook.variable_type(data)
            variable = sd.get('variable')

            if data_type == 'Binary':
                data = self._decode_binary(data, variable)
            elif data_type == 'BinaryArray':
                data = [self._decode_binary(d, variable) for d in data]
                # decoded_data = []
                # for d in data:
                #     decoded_data.append(self._decode_binary(d, variable))
                # data = decoded_data
            self.provider.tcex.playbook.create(variable, data)

    def stage(self, variable, data):
        """Stage data in redis"""
        self.provider.tcex.playbook.create(variable, data)

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


class ThreatConnect(object):
    """Stages the ThreatConnect Data"""

    def __init__(self, provider):
        self.provider = provider
        self.batch = None

    def dir(self, directory, owner, batch=False):
        """Stages the directory"""
        entities = []
        for stage_file in os.listdir(directory):
            if not (stage_file.endswith('.json') and stage_file.startswith('tc_stage_')):
                continue
            entities.append(self._convert_to_entities(stage_file))
        return self.entities(entities, owner, batch=batch)

    def file(self, file, owner, batch=False):
        """Stages the file"""
        entities = self._convert_to_entities(file)
        return self.entities(entities, owner, batch=batch)

    def entities(self, entities, owner, batch=False):
        """Stages all of the provided entities"""
        response = []
        if batch:
            self.batch = self.provider.tcex.batch(owner)
            for entity in entities:
                self.batch.save(self._convert_to_batch_entity(entity))
                response = self.batch.submit_all()
        else:
            for entity in entities:
                response.append(self.entity(entity, owner))
        return response if not batch else None

    def entity(self, entity, owner):
        """Stage data in ThreatConnect"""

    def _convert_to_entities(self, file):
        """Convert A file to TC Entity's"""
        return self.batch or file

    def _convert_to_batch_entity(self, entity):
        """Convert TC Entity to a Batch entity"""
