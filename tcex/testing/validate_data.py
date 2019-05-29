# -*- coding: utf-8 -*-
"""Validate Data Testing Module"""
import operator
import hashlib
import os
import json


class Validator(object):
    """Validator"""

    def __init__(self, tcex):
        self.tcex = tcex
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

    def type(self, variable, redis_type):
        """validates the type of a redis variable"""
        if not variable or not redis_type:
            return False
        if redis_type not in self.provider.tcex.playbook.read_data_types():
            return 'You messed up'
        if redis_type != self.provider.tcex.playbook.variable_type(variable):
            return False
        variable_data = self.provider.tcex.playbook.read(variable)
        if not variable_data:
            return False
        if variable_data.get('type', None) != redis_type:
            return False

        return True

    def data(self, variable, data, op='='):
        """validates that the redis variable matches the provided op of the data"""
        if not variable:
            return False
        op = self.provider.get_operator(op)
        if not operator:
            return False
        variable_data = self.provider.tcex.playbook.read(variable)
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

    def tc_entities(self, tc_entities, owner):
        """validates a array of tc_entitites"""
        results = []
        for entity in tc_entities:
            results.append(self.tc_entity(entity, owner))
        return results

    def tc_entity(self, tc_entity, owner):
        """validates the ti_response entity"""
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        response = {'valid': True, 'errors': []}
        ti_entity = self._convert_to_ti_entity(tc_entity, owner)
        ti_response = ti_entity.single(params=parameters)
        ti_response = ti_response.json()
        response.get('errors').append(self._response_attributes(ti_response, tc_entity))
        response.get('errors').append(self._response_tags(ti_response, tc_entity))
        response.get('errors').append(self._response_labels(ti_response, tc_entity))
        response.get('errors').append(self._file(tc_entity))

        if ti_entity.type == 'Indicator':
            provided_rating = ti_entity.data.get('rating', None)
            expected_rating = ti_response.get('rating', None)
            if not provided_rating == expected_rating:
                response.get('errors').append(
                    'RatingError: Provided rating {} does not match '
                    'actual rating {}'.format(provided_rating, expected_rating)
                )

            provided_confidence = ti_entity.data.get('confidence', None)
            expected_confidence = ti_response.get('confidence', None)
            if not provided_confidence == expected_confidence:
                response.get('errors').append(
                    'ConfidenceError: Provided confidence {} does not match '
                    'actual confidence {}'.format(provided_rating, expected_rating)
                )
            provided_summary = ti_entity.unique_id
            expected_summary = ti_response.get('summary', None)
            if not provided_summary == expected_summary:
                response.get('errors').append(
                    'SummaryError: Provided summary {} does not match '
                    'actual summary {}'.format(provided_summary, expected_summary)
                )
        elif ti_entity.type == 'Group':
            provided_summary = ti_entity.data.get('name', None)
            expected_summary = ti_response.get('summary', None)
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
            print(response['errors'])
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

        print('Attribute errors: ', errors)

        return errors

    @staticmethod
    def compare_lists(expected, actual):
        """Compares two lists and returns a list of errors if they don't match"""
        errors = []
        for item in expected:
            if item in expected:
                del actual[item]
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
                group_type=tc_entity.get('type'), owner=owner, unique_id=tc_entity.get('summary')
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
            actual.append(tag)
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
            actual.append(tag)
        errors = self.compare_lists(expected, actual)
        errors = ['SecurityLabelError: ' + error for error in errors]

        return errors

    @staticmethod
    def _file(ti_entity):
        errors = []
        if ti_entity.get('type') == 'Document' or ti_entity.get('type') == 'Report':
            downloaded = ti_entity.download()
            return hashlib.md5(open(downloaded, 'rb').read()).hexdigest()
            # file_hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
            # if downloaded_hash != file_hash:
            #     errors.append(
            #         'Hash of saved file {} does not match provided '
            #         'file hash {}'.format(downloaded_hash, file_hash)
            #     )
        return errors
