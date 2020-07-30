# -*- coding: utf-8 -*-
"""Stage Data Testing Module"""
# standard library
import base64
import binascii
import json
import os
import sys


# pylint: disable=no-self-use
class Stager:
    """Stage Data class"""

    def __init__(self, tcex, log):
        """Initialize class properties"""
        # self.args = tcex.args  # required for args to be parsed
        self.log = log
        self.tcex = tcex
        # TODO: validate this
        self.tcex.logger.update_handler_level('error')

        # properties
        self._redis = None
        self._threatconnect = None

    @property
    def redis(self):
        """Get the current instance of Redis for staging data"""
        if not self._redis:
            self._redis = Redis(self)
        return self._redis

    @property
    def threatconnect(self):
        """Get the current instance of ThreatConnect for staging data"""
        if not self._threatconnect:
            self._threatconnect = ThreatConnect(self)
        return self._threatconnect


class Redis:
    """Stages the Redis Data"""

    def __init__(self, provider):
        """Initialize class properties."""
        self.provider = provider
        self.redis_client = provider.tcex.redis_client
        self.log = self.provider.log

    def from_dict(self, staging_data):
        """Stage redis data from dict"""
        for variable, data in staging_data.items():
            variable_type = self.provider.tcex.playbook.variable_type(variable)

            self.log.data('stage', 'variable', variable)
            self.log.data('stage', 'data', data)
            if data is not None and variable_type == 'Binary':
                data = self._decode_binary(data, variable)
            elif data is not None and variable_type == 'BinaryArray':
                data = [self._decode_binary(d, variable) for d in data]
            self.provider.tcex.playbook.create(variable, data)

    def stage(self, variable, data):
        """Stage data in redis"""
        self.provider.tcex.playbook.create(variable, data)

    def delete_context(self, context):
        """Delete data in redis"""
        keys = self.redis_client.hkeys(context)
        if keys:
            return self.redis_client.hdel(context, *keys)
        return 0

    @staticmethod
    def _decode_binary(binary_data, variable):
        """Base64 decode binary data."""
        try:
            data = None
            if binary_data is not None:
                data = base64.b64decode(binary_data)
        except binascii.Error as e:
            print(
                f'The Binary staging data for variable {variable} is not properly base64 encoded '
                f'due to {e}'
            )
            sys.exit()
        return data


class ThreatConnect:
    """Stages the ThreatConnect Data"""

    def __init__(self, provider):
        """Initialize Class properties."""
        self.provider = provider
        self.batch = None

    def dir(self, directory, owner, batch=False):
        """Stages the directory"""
        entities = []
        for stage_file in os.listdir(directory):
            if not (stage_file.endswith('.json') and stage_file.startswith('tc_stage_')):
                continue
            entities.append(self._convert_to_entities(f'{directory}/{stage_file}'))
        return self.entities(entities, owner, batch=batch)

    def file(self, file, owner, batch=False):
        """Stages the file"""
        entities = self._convert_to_entities(file)
        return self.entities(entities, owner, batch=batch)

    def entities(self, entities, owner=None, batch=False):
        """Stages all of the provided entities"""
        response = []
        if batch:
            self.batch = self.provider.tcex.batch(owner)
            for key, entity in entities.items():
                labels = entity.pop('securityLabels')
                attributes = entity.pop('attributes')
                tags = entity.pop('tags')
                associations = entity.pop('associations')
                entity['xid'] = entity.get(
                    'xid',
                    self.provider.batch.generate_xid(
                        [owner, entity.get('type'), entity.get('summary')]
                    ),
                )
                batch_entity = self._convert_to_batch_entity(entity)
                self.provider.batch.save(batch_entity)
                for tag in tags:
                    batch_entity.tag(tag)
                for label in labels:
                    batch_entity.label(label)
                for association in associations:
                    batch_entity.association(association)
                for attribute in attributes:
                    batch_entity.attribute(
                        attribute.get('type'),
                        attribute.get('value'),
                        attribute.get('displayed', True),
                    )

            response = self.batch.submit_all()
        else:
            for key, value in entities.items():
                response.append(self.entity(key, value, owner))
        return response if not batch else None

    def entity(self, key, value, owner=None):
        """Stage data in ThreatConnect"""
        owner = value.pop('owner', None) or owner
        created_entity = self.provider.tcex.cm.create_entity(value, owner)
        if created_entity is None:
            # This is here because there is a type `Task` in both TI and CM
            if value.get('type', '').lower().startswith('ti_'):
                value['type'] = value.get('type')[3:]
            created_entity = self.provider.tcex.ti.create_entity(value, owner)
        return {'key': key, 'data': created_entity}

    def delete_staged(self, staged_data):
        """Delete data in redis"""
        for data in staged_data:
            data = data.get('data', {})
            if data.get('status_code') != 201:
                continue

            entity_type = data.pop('main_type')
            ti = None
            if entity_type == 'Group':
                ti = self.provider.tcex.ti.group(data.get('sub_type'), owner=data.get('owner'))
                data = data.get(ti.api_entity) or data
                ti._set_unique_id(data)
            elif entity_type == 'Indicator':
                ti = self.provider.tcex.ti.indicator(data.get('sub_type'), owner=data.get('owner'))
                data = data.get(ti.api_entity) or data
                ti._set_unique_id(data)
            elif entity_type == 'Task':
                ti = self.provider.tcex.ti.task(owner=data.get('owner'))
                data = data.get(ti.api_entity) or data
                ti._set_unique_id(data)
            elif entity_type == 'Victim':
                ti = self.provider.tcex.ti.victim(owner=data.get('owner'))
                data = data.get(ti.api_entity) or data
                ti._set_unique_id(data)
            if ti:
                ti.delete()
            if entity_type == 'Case_Management':
                cm = getattr(self.provider.tcex.cm, data.get('sub_type'))()
                if data.get('sub_type').lower() in [
                    'workflow_event',
                    'workflowevent',
                    'workflow event',
                ]:
                    continue
                cm.id = data.get('id')
                cm.delete()

    def clear(self, owner):
        """Delete and recreate the owner"""

    @staticmethod
    def _convert_to_entities(file):
        """Convert A file to TC Entity's"""
        with open(file, 'r') as read_file:
            data = json.load(read_file)
        return data

    def _convert_to_batch_entity(self, entity):
        """Convert TC Entity to a Batch entity"""
        entity_type = entity.pop('type')
        ti = None
        if entity_type in self.provider.tcex.indicator_types:
            ti = self.provider.batch.indicator(entity_type, entity.pop('summary'), entity)
        elif entity_type in self.provider.tcex.group_types:
            ti = self.provider.batch.group(entity_type, entity.pop('summary'), entity)
        return ti
