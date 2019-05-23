# -*- coding: utf-8 -*-
"""Validate Data Testing Module"""
import operator
import hashlib
import os


class Validator(object):
    """Validator"""

    def __init__(self, tcex):
        self.tcex = tcex
        self.redis = Redis(tcex)
        self.threatconnect = ThreatConnect(tcex)

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


class Redis(Validator):
    """Validates Redis data"""

    def type(self, variable, redis_type):
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

    def data(self, variable, data, op='='):
        """validates that the redis variable matches the provided op of the data"""
        if not variable:
            return False
        op = self.get_operator(op)
        if not operator:
            return False
        variable_data = self.tcex.playbook.read(variable)
        return op(variable_data, data)

    def eq(self, variable, data):
        """tests equation of redis var"""
        return self.data(variable, data)

    def gt(self, variable, data):
        """tests gt of redis var"""
        return self.data(variable, data, op='>')

    def lt(self, variable, data):
        """tests lt of redis var"""
        return self.data(variable, data, op='<')


class ThreatConnect(Validator):
    """Validate ThreatConnect data"""

    def __init__(self, tcex):
        super(ThreatConnect, self).__init__(tcex)
        self.seeded_file = None
        self.static_files = None

    def dir(self, directory):
        """validates the content of a given dir"""
        results = []
        for test_file in os.listdir(directory):
            if not (test_file.endswith('.json') and test_file.startswith('validate_')):
                continue
            results.append(self.file(test_file))
        return results

    # def seeded_file(self):
    #     """validates the content of the seeded file"""
    #     return self.file(self.seeded_file)
    #
    # def static_file(self):
    #     """validates the content of the static file"""
    #     return self.file(self.static_file)

    def file(self, file):
        """validates the content of a given file"""
        entities, files = self._convert_to_entities(file)
        return self.tc_entities(entities, files)

    def tc_entities(self, tc_entities, files=None):
        """validates a array of tc_entitites"""
        results = []
        if files and len(files) != len(tc_entities):
            return [{'valid': False, 'errors': 'File length did not match tc_entity length'}]
        for index, entity in enumerate(tc_entities):
            file = None
            if files:
                file = files[index]
            results.append(self.tc_entity(entity, file))
        return results

    def tc_entity(self, tc_entity, file=None):
        """validates the ti_response entity"""
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        response = {'valid': True, 'errors': []}
        ti_entity = self._convert_to_ti_entity(tc_entity)
        ti_response = ti_entity.single(parameters)
        response.get('errors').append(self._response_attributes(ti_response, ti_entity))
        response.get('errors').append(self._response_tags(ti_response, ti_entity))
        response.get('errors').append(self._response_labels(ti_response, ti_entity))
        response.get('errors').append(self._file(ti_entity, file))
        # Handle stuff like the rating/confidence/name/ip/ext. Specific things unique to each ti
        # object type.

        if response.get('errors'):
            response['valid'] = False

        return response

    @staticmethod
    def _convert_to_entities(file):
        """converts file to tc_entity array"""
        if not file:
            return file
        return file

    def _convert_to_ti_entity(self, tc_entity):
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

    @staticmethod
    def _response_attributes(ti_response, tc_entity):
        """validates the ti_response attributes"""
        errors = []
        if ti_response or tc_entity:
            return errors

        return errors

    @staticmethod
    def _response_tags(ti_response, tc_entity):
        """validates the ti_response tags"""
        errors = []
        if ti_response or tc_entity:
            return errors

        return errors

    @staticmethod
    def _response_labels(ti_response, tc_entity):
        """validates the ti_response labels"""
        errors = []
        if ti_response or tc_entity:
            return errors

        return errors

    @staticmethod
    def _file(ti_entity, file):
        errors = []
        if (ti_entity.type == 'Document' or ti_entity.type == 'Report') and file:
            downloaded = ti_entity.download()
            downloaded_hash = hashlib.md5(open(downloaded, 'rb').read()).hexdigest()
            file_hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
            if downloaded_hash != file_hash:
                errors.append(
                    'Hash of saved file {} does not match provided '
                    'file hash {}'.format(downloaded_hash, file_hash)
                )
        return errors
