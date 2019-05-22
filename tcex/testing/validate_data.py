# -*- coding: utf-8 -*-
"""Validate Data Testing Module"""
import operator
import hashlib
import os


class ValidateData(object):
    """Validate Data class"""

    def __init__(self, tcex):
        self.tcex = tcex
        self.seeded_file = None
        self.static_file = None

    @staticmethod
    def get_operator(op):
        """gets the corresponding operator"""
        operators = {
            'lt': operator.lt,
            '<': operator.lt,
            'le': operator.le,
            '<=': operator.le,
            'eq': operator.eq,
            '=': operator.eq,
            'ne': operator.ne,
            '!=': operator.ne,
            'ge': operator.ge,
            '>=': operator.ge,
            'gt': operator.gt,
            '>': operator.gt,
        }
        return operators.get(op, None)

    def validate_redis(self, variable, data, op='='):
        """validates the redis data with a given op"""
        if not variable:
            return False
        op = self.get_operator(op)
        if not operator:
            return False
        variable_data = self.tcex.playbook.read(variable)
        return op(variable_data, data)

    def validate_redis_type(self, variable, redis_type):
        """validates the type of a redis variable"""
        if not variable or not redis_type:
            return False
        if redis_type not in self.tcex.playbook.read_data_types():
            return 'You messed up'
        if redis_type != self.tcex.playbook.variable_type(variable):
            return False
        variable_data = self.tcex.playbook.read(variable)
        if not variable_data:
            return False
        if variable_data.get('type', None) != redis_type:
            return False

        return True

    def validate_redis_eq(self, variable, data):
        """tests equation of redis var"""
        return self.validate_redis(variable, data)

    def validate_redis_gt(self, variable, data):
        """tests gt of redis var"""
        return self.validate_redis(variable, data, op='>')

    def validate_redis_lt(self, variable, data):
        """tests lt of redis var"""
        return self.validate_redis(variable, data, op='<')

    def _convert_file_to_entities(self, file):
        """converts file to tc_entity array"""
        if not file:
            file = self.seeded_file
        return file

    def validate_file(self, file):
        """validates the content of a given file"""
        entities = self._convert_file_to_entities(file)
        return self.validate_tc_entities(entities)

    def validate_dir(self, directory):
        """validates the content of a given dir"""
        results = []
        for test_file in os.listdir(directory):
            if not test_file.endswith('.json'):
                continue
            results.append(self.validate_file(test_file))
        return results

    def validate_seeded_file(self):
        """validates the content of the seeded file"""
        return self.validate_file(self.seeded_file)

    def validate_static_file(self):
        """validates the content of the static file"""
        return self.validate_file(self.static_file)

    def validate_tc_entities(self, tc_entities, files=None):
        """validates a array of tc_entitites"""
        if files and len(files) != len(tc_entities):
            print('you messed up')
            return False
        results = []
        for index, entity in enumerate(tc_entities):
            file = None
            if files:
                file = files[index]
            results.append(self.validate_tc_entity(entity, file))
        return results

    def _convert_tc_entity_to_ti_entity(self, tc_entity):
        """converts a tc_entity to a ti_entity"""
        ti_entity = None
        if tc_entity.type.is_indicator:
            ti_entity = self.tcex.ti.indicator(
                indicator_type=tc_entity.type, owner=tc_entity.owner, unique_id=tc_entity.unique_id
            )
        elif tc_entity.type.is_group:
            ti_entity = self.tcex.ti.group(
                group_type=tc_entity.type, owner=tc_entity.owner, unique_id=tc_entity.unique_id
            )
        elif tc_entity.type.is_victim:
            ti_entity = self.tcex.ti.victim(unique_id=tc_entity.unique_id, owner=tc_entity.owner)

        return ti_entity

    def validate_ti_response_attributes(self, ti_response, tc_entity):
        """validates the ti_response attributes"""

    def validate_ti_response_tags(self, ti_response, tc_entity):
        """validates the ti_response tags"""

    def validate_ti_response_labels(self, ti_response, tc_entity):
        """validates the ti_response labels"""

    def validate_tc_entity(self, tc_entity, file=None):
        """validates the ti_response entity"""
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        response = {'valid': True, 'errors': []}
        ti_entity = self._convert_tc_entity_to_ti_entity(tc_entity)
        ti_response = ti_entity.single(parameters)
        if not self.validate_ti_response_attributes(ti_response, tc_entity):
            response.get('errors').append(
                'Attributes of saved item {} does not match tc_entity {}'.format(
                    ti_response, tc_entity
                )
            )
        if not self.validate_ti_response_tags(ti_response, tc_entity):
            response.get('errors').append(
                'Tags of saved item {} does not match tc_entity {}'.format(ti_response, tc_entity)
            )
        if not self.validate_ti_response_labels(ti_response, tc_entity):
            response.get('errors').append(
                'Security Labels of saved item {} does not match '
                'tc_entity {}'.format(ti_response, tc_entity)
            )
        # Handle stuff like the rating/confidence/name/ip/ext. Specific things unique to each ti
        # object type.
        if (ti_entity.type == 'Document' or ti_entity.type == 'Report') and file:
            downloaded = ti_entity.download()
            downloaded_hash = hashlib.md5(open(downloaded, 'rb').read()).hexdigest()
            file_hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
            if downloaded_hash != file_hash:
                response.get('errors').append(
                    'Hash of saved file {} does not match provided '
                    'file hash {}'.format(downloaded_hash, file_hash)
                )

        if response.get('errors'):
            response['valid'] = False

        return response
