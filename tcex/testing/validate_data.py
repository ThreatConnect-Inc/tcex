# -*- coding: utf-8 -*-
"""Validate Data Testing Module"""
import operator
import hashlib
import os
import json


class Validator(object):
    """Validator"""

    def __init__(self, tcex, log):
        # self.args = tcex.args
        self.log = log
        self.tcex = tcex

        # properties
        self._redis = None
        self._threatconnect = None

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

    @property
    def redis(self):
        """Gets the current instance of Redis for validating data"""
        if not self._redis:
            self._redis = Redis(self)
        return self._redis

    @property
    def threatconnect(self):
        """Gets the current instance of ThreatConnect for validating data"""
        if not self._threatconnect:
            self._threatconnect = ThreatConnect(self)
        return self._threatconnect


class Redis(object):
    """Validates Redis data"""

    def __init__(self, provider):
        self.provider = provider
        self.redis_client = provider.tcex.playbook.db.r

    def not_null(self, variable):
        """validates that a variable is not empty/null"""
        # Could do something like self.ne(variable, None), but want to be pretty specific on
        # the errors on this one
        response = {'valid': True, 'errors': []}
        if not variable:
            response.get('errors').append('NoneError: Redis Variable not provided')
        else:
            variable_data = self.provider.tcex.playbook.read(variable)
            if not variable_data:
                response.get('errors').append(
                    'NullError: Variable {} not found or empty'.format(variable)
                )
        if response.get('errors'):
            response['valid'] = False

        return response

    def type(self, variable, redis_type):
        """validates the type of a redis variable"""
        response = {'valid': True, 'errors': []}
        if not variable:
            response.get('errors').append('NoneError: Redis Variable not provided')
        elif not redis_type:
            response.get('errors').append('NoneError: Redis Type not provided')
        elif redis_type not in self.provider.tcex.playbook.read_data_types():
            response.get('errors').append('InvalidTypeError: Redis Type not supported')
        elif redis_type != self.provider.tcex.playbook.variable_type(variable):
            response.get('errors').append(
                'TypeMismatchError: Redis Type: {} and Variable Type: {} do not match'.format(
                    redis_type, self.provider.tcex.playbook.variable_type(variable)
                )
            )
        else:
            variable_data = self.provider.tcex.playbook.read(variable)
            if not variable_data:
                response.get('errors').append(
                    'NotFoundError: Variable {} not found'.format(variable)
                )
            if variable_data.get('type', None) != redis_type:
                response.get('errors').append(
                    'TypeMismatchError: Redis Type: {} and Variable Type: {} do not match'.format(
                        redis_type, self.provider.tcex.playbook.variable_type(variable)
                    )
                )
        if response.get('errors'):
            response['valid'] = False

        return response

    def data(self, variable, data, op=None):
        """Validate Redis data <operator> variable_data.

        Args:
            variable (str): The variable to read from REDIS.
            data (dict or list or str): The validation data
            op (str, optional): The comparison operator expression. Defaults to "eq".

        Returns:
            [type]: [description]
        """
        op = op or 'eq'
        if not variable:
            self.provider.log.error('NoneError: Redis Variable not provided')
            return False

        if not self.provider.get_operator(op):
            self.provider.log.error('Invalid operator provided ({})'.format(op))
            return False

        variable_data = self.provider.tcex.playbook.read(variable)

        # Logging
        self.provider.log.info('[validator] Variable: {}'.format(variable))
        self.provider.log.info('[validator] DB Data: {}'.format(variable_data))
        self.provider.log.info('[validator] User Data: {}'.format(data))
        self.provider.log.debug(
            'redis-cli hget {} \'{}\''.format(
                self.provider.tcex.args.tc_playbook_db_context, variable
            )
        )
        return self.provider.get_operator(op)(variable_data, data)

    def eq(self, variable, data):
        """tests equation of redis var"""
        return self.data(variable, data)

    def gt(self, variable, data):
        """tests gt of redis var"""
        return self.data(variable, data, op='gt')

    def lt(self, variable, data):
        """tests lt of redis var"""
        return self.data(variable, data, op='lt')

    def le(self, variable, data):
        """tests le of redis var"""
        return self.data(variable, data, op='le')

    def ne(self, variable, data):
        """tests ne of redis var"""
        return self.data(variable, data, op='ne')

    def ge(self, variable, data):
        """tests ge of redis var"""
        return self.data(variable, data, op='ge')


class ThreatConnect(object):
    """Validate ThreatConnect data"""

    def __init__(self, provider):
        self.provider = provider

    def dir(self, directory, owner):
        """validates the content of a given dir"""
        results = []
        for test_file in os.listdir(directory):
            if not (test_file.endswith('.json') and test_file.startswith('validate_')):
                continue
            results.append(self.file('{}/{}'.format(directory, test_file), owner))
        return results

    def file(self, file, owner):
        """validates the content of a given file"""
        entities = self._convert_to_entities(file)
        return self.tc_entities(entities, owner)

    def tc_entities(self, tc_entities, owner, files=None):
        """validates a array of tc_entitites"""
        results = []
        if files:
            if not len(tc_entities) == len(files):
                return {
                    'valid': True,
                    'errors': [
                        'LengthError: Length of files provided does not '
                        'match length of entities provided.'
                    ],
                }

        for index, entity in enumerate(tc_entities):
            if files:
                results.append(self.tc_entity(entity, owner, files[index]))
            results.append(self.tc_entity(entity, owner))
        return results

    def tc_entity(self, tc_entity, owner, file=None):
        """validates the ti_response entity"""
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        response = {'valid': True, 'errors': []}
        ti_entity = self._convert_to_ti_entity(tc_entity, owner)
        ti_response = ti_entity.single(params=parameters)
        if not self.success(ti_response):
            response.get('errors').append(
                'NotFoundError: Provided entity {} could not be fetched from ThreatConnect'.format(
                    tc_entity.get('summary')
                )
            )
        else:
            ti_response_entity = None
            ti_response = ti_response.json().get('data', {}).get(ti_entity.api_entity, {})
            for entity in self.provider.tcex.ti.entities(ti_response, tc_entity.get('type', None)):
                ti_response_entity = entity
            response.get('errors').append(self._response_attributes(ti_response, tc_entity))
            response.get('errors').append(self._response_tags(ti_response, tc_entity))
            response.get('errors').append(self._response_labels(ti_response, tc_entity))
            response.get('errors').append(self._file(ti_entity, file))

            if ti_entity.type == 'Indicator':
                provided_rating = tc_entity.get('rating', None)
                expected_rating = ti_response.get('rating', None)
                if not provided_rating == expected_rating:
                    response.get('errors').append(
                        'RatingError: Provided rating {} does not match '
                        'actual rating {}'.format(provided_rating, expected_rating)
                    )

                provided_confidence = tc_entity.get('confidence', None)
                expected_confidence = ti_response.get('confidence', None)
                if not provided_confidence == expected_confidence:
                    response.get('errors').append(
                        'ConfidenceError: Provided confidence {} does not match '
                        'actual confidence {}'.format(provided_confidence, expected_confidence)
                    )
                provided_summary = ti_entity.unique_id
                expected_summary = ti_response_entity.get('value', None)
                if not provided_summary == expected_summary:
                    response.get('errors').append(
                        'SummaryError: Provided summary {} does not match '
                        'actual summary {}'.format(provided_summary, expected_summary)
                    )
            elif ti_entity.type == 'Group':
                provided_summary = tc_entity.get('summary', None)
                expected_summary = ti_response_entity.get('value', None)
                if not provided_summary == expected_summary:
                    response.get('errors').append(
                        'SummaryError: Provided summary {} does not match '
                        'actual summary {}'.format(provided_summary, expected_summary)
                    )

        response['errors'] = self.flatten(response['errors'])
        if response.get('errors'):
            response['errors'].insert(
                0, 'Errors for Provided Entity: {}'.format(tc_entity.get('summary'))
            )
            response['valid'] = False

        return response

    def flatten(self, lis):
        """Idk why python doesnt have this built in but helper function to flatten a list"""
        new_lis = []
        for item in lis:
            if isinstance(item, list):
                new_lis.extend(self.flatten(item))
            else:
                new_lis.append(item)
        return new_lis

    @staticmethod
    def compare_dicts(expected, actual):
        """Compares two dicts and returns a list of errors if they don't match"""
        errors = []
        for item in expected:
            if item in actual:
                if expected.get(item) == actual.get(item):
                    actual.pop(item)
                    continue
                errors.append(
                    '{0} : {1} did not match {0} : {2}'.format(
                        item, expected.get('item'), actual.get(item)
                    )
                )
                actual.pop(item)
            else:
                errors.append(
                    '{} : {} was in expected results but not in actual results.'.format(
                        item, expected.get(item)
                    )
                )
        for item in actual.items():
            errors.append(
                '{} : {} was in actual results but not in expected results.'.format(
                    item, actual.get(item)
                )
            )

        return errors

    @staticmethod
    def compare_lists(expected, actual):
        """Compares two lists and returns a list of errors if they don't match"""
        errors = []
        for item in expected:
            if item in actual:
                actual.remove(item)
            else:
                errors.append('{} was in expected results but not in actual results.'.format(item))
        for item in actual:
            errors.append('{} was in actual results but not in expected results.'.format(item))

        return errors

    @staticmethod
    def _convert_to_entities(file):
        """converts file to tc_entity array"""
        with open(file, 'r') as read_file:
            data = json.load(read_file)
        return data

    def _convert_to_ti_entity(self, tc_entity, owner):
        """converts a tc_entity to a ti_entity"""
        ti_entity = None
        if tc_entity.get('type') in self.provider.tcex.indicator_types:
            ti_entity = self.provider.tcex.ti.indicator(
                indicator_type=tc_entity.get('type'),
                owner=owner,
                unique_id=tc_entity.get('summary'),
            )
        elif tc_entity.get('type') in self.provider.tcex.group_types:
            ti_entity = self.provider.tcex.ti.group(
                group_type=tc_entity.get('type'), owner=owner, unique_id=tc_entity.get('id')
            )
        elif tc_entity.get('type') == 'Victim':
            ti_entity = self.provider.tcex.ti.victim(
                unique_id=tc_entity.get('summary'), owner=owner
            )

        return ti_entity

    def _response_attributes(self, ti_response, tc_entity):
        """validates the ti_response attributes"""
        if not ti_response or not tc_entity:
            return []

        expected = {}
        actual = {}
        for attribute in tc_entity.get('attribute', []):
            expected[attribute.get('type')] = attribute.get('value')
        for attribute in ti_response.get('attribute', []):
            actual[attribute.get('type')] = attribute.get('value')
        errors = self.compare_dicts(expected, actual)
        errors = ['AttributeError: ' + error for error in errors]

        return errors

    def _response_tags(self, ti_response, tc_entity):
        """validates the ti_response tags"""
        errors = []
        if not ti_response or not tc_entity:
            return errors

        expected = []
        actual = []
        for tag in tc_entity.get('tag', []):
            expected.append(tag)
        for tag in ti_response.get('tag', []):
            actual.append(tag.get('name'))
        errors = self.compare_lists(expected, actual)
        errors = ['TagError: ' + error for error in errors]

        return errors

    def _response_labels(self, ti_response, tc_entity):
        """validates the ti_response labels"""
        errors = []
        if not ti_response or not tc_entity:
            return errors

        expected = []
        actual = []
        for tag in tc_entity.get('securityLabel', []):
            expected.append(tag)
        for tag in ti_response.get('securityLabel', []):
            actual.append(tag.get('name'))
        errors = self.compare_lists(expected, actual)
        errors = ['SecurityLabelError: ' + error for error in errors]

        return errors

    @staticmethod
    def _file(ti_entity, file):
        errors = []
        if ti_entity.api_sub_type == 'Document' or ti_entity.api_sub_type == 'Report':
            actual_hash = ti_entity.get_file_hash()
            actual_hash = actual_hash.hexdigest()
            provided_hash = hashlib.sha256()
            with open(file, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    provided_hash.update(byte_block)
            provided_hash = provided_hash.hexdigest()
            if not provided_hash == actual_hash:
                errors.append(
                    'sha256 {} of provided file did not match sha256 of actual file {}'.format(
                        provided_hash, actual_hash
                    )
                )
        else:
            errors.append(
                'TypeError: {} entity type does not contain files.'.format(ti_entity.api_sub_type)
            )
        return errors

    @staticmethod
    def success(r):
        """

        Args:
            r:

        Return:

        """
        status = True
        if r.ok:
            try:
                if r.json().get('status') != 'Success':
                    status = False
            except Exception:
                status = False
        else:
            status = False
        return status
