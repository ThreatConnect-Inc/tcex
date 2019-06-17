# -*- coding: utf-8 -*-
"""Validate Data Testing Module"""
import hashlib
import json
import operator
import os
import re
from six import string_types


class Validator(object):
    """Validator"""

    def __init__(self, tcex, log):
        """Initialize class properties."""
        self.log = log
        self.tcex = tcex

        # properties
        self._redis = None
        self._threatconnect = None

    def get_operator(self, op):
        """Get the corresponding operator"""
        operators = {
            'dd': self.operator_deep_diff,
            'eq': operator.eq,
            '=': operator.eq,
            'le': operator.le,
            '<=': operator.le,
            'lt': operator.lt,
            '<': operator.lt,
            'ge': operator.ge,
            '>=': operator.ge,
            'gt': operator.gt,
            '>': operator.gt,
            'jeq': self.operator_json_eq,
            'json_eq': self.operator_json_eq,
            'kveq': self.operator_keyvalue_eq,
            'keyvalue_eq': self.operator_keyvalue_eq,
            'ne': operator.ne,
            '!=': operator.ne,
            'rex': self.operator_regex_match,
        }
        return operators.get(op, None)

    def operator_deep_diff(self, app_data, test_data):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.
            exclude_keys (list, kwargs): A list of key for a KeyValueArray to be removed.

        Returns:
            bool: The results of the operator.
        """
        try:
            from deepdiff import DeepDiff
        except ImportError:
            self.log.error('Could not import DeepDiff module (try "pip install deepdiff").')
            return False

        # run operator
        try:
            ddiff = DeepDiff(app_data, test_data, ignore_order=True)
        except KeyError:
            return False
        except NameError:
            return False
        if ddiff:
            self.log.info('[validator] Diff: {}'.format(ddiff))
            return False
        return True

    def operator_json_eq(self, app_data, test_data, **kwargs):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.

        Returns:
            bool: The results of the operator.
        """
        if isinstance(app_data, (string_types)):
            app_data = json.loads(app_data)
        if isinstance(test_data, (string_types)):
            test_data = json.loads(test_data)

        # remove exclude field. usually dynamic data like date fields.
        for e in kwargs.get('exclude', []):
            try:
                del app_data[e]
            except KeyError:
                pass

            try:
                del test_data[e]
            except KeyError:
                pass
        return self.operator_deep_diff(app_data, test_data)

    def operator_keyvalue_eq(self, app_data, test_data, **kwargs):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.

        Returns:
            bool: The results of the operator.
        """
        # remove exclude_key field. usually dynamic data like date fields.
        if kwargs.get('exclude_keys') is not None:
            app_data = [
                kv for kv in app_data if kv.get('key') not in kwargs.get('exclude_keys', [])
            ]
            test_data = [
                kv for kv in test_data if kv.get('key') not in kwargs.get('exclude_keys', [])
            ]
        return self.operator_deep_diff(app_data, test_data, **kwargs)

    @staticmethod
    def operator_regex_match(app_data, test_data):
        """Compare app data equals tests data.

        Args:
            app_data (dict|str|list): The data created by the App.
            test_data (dict|str|list): The data provided in the test case.

        Returns:
            bool: The results of the operator.
        """
        return re.match(test_data, app_data)

    @property
    def redis(self):
        """Get the current instance of Redis for validating data"""
        if not self._redis:
            self._redis = Redis(self)
        return self._redis

    @property
    def threatconnect(self):
        """Get the current instance of ThreatConnect for validating data"""
        if not self._threatconnect:
            self._threatconnect = ThreatConnect(self)
        return self._threatconnect


class Redis(object):
    """Validates Redis data"""

    def __init__(self, provider):
        """Initialize class properties."""
        self.provider = provider
        self.redis_client = provider.tcex.playbook.db.r

    def not_null(self, variable):
        """Validate that a variable is not empty/null"""
        # Could do something like self.ne(variable, None), but want to be pretty specific on
        # the errors on this one
        variable_data = self.provider.tcex.playbook.read(variable)
        self.provider.log.info('[validator] Variable: {}'.format(variable))
        self.provider.log.info('[validator] DB Data: {}'.format(variable_data))
        if not variable:
            self.provider.log.error('NoneError: Redis Variable not provided')
            return False

        if not variable_data:
            self.provider.log.error(
                'NotFoundError: Redis Variable {} was not found.'.format(variable)
            )
            return False

        return True

    def type(self, variable):
        """Validate the type of a redis variable"""
        variable_data = self.provider.tcex.playbook.read(variable)
        self.provider.log.info('[validator] Variable: {}'.format(variable))
        self.provider.log.info('[validator] App Data:  {}'.format(variable_data))
        redis_type = self.provider.tcex.playbook.variable_type(variable)
        if redis_type.endswith('Array'):
            redis_type = list
        elif redis_type.startswith('String'):
            redis_type = str
        elif redis_type.startswith('KeyValuePair'):
            redis_type = dict
        else:
            redis_type = str

        if not variable_data:
            self.provider.log.error(
                'NotFoundError: Redis Variable {} was not found.'.format(variable)
            )
            return False
        if not isinstance(variable_data, redis_type):
            self.provider.log.error(
                'TypeMismatchError: Redis Type: {} and Variable: {} '
                'do not match'.format(redis_type, variable)
            )
            return False

        return True

    def data(self, variable, test_data, op=None, **kwargs):
        """Validate Redis data <operator> test_data.

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

        if variable.endswith('Binary'):
            app_data = self.provider.tcex.playbook.read_binary(variable, False, False)
        elif variable.endswith('BinaryArray'):
            app_data = self.provider.tcex.playbook.read_binary_array(variable, False, False)
        else:
            app_data = self.provider.tcex.playbook.read(variable)

        # Logging
        self.provider.log.info('[validator] Variable:  {}'.format(variable))
        self.provider.log.info('[validator] App Data:  {}'.format(app_data))
        self.provider.log.info('[validator] Test Data: {}'.format(test_data))
        self.provider.log.debug(
            'redis-cli hget {} \'{}\''.format(
                self.provider.tcex.args.tc_playbook_db_context, variable
            )
        )
        return self.provider.get_operator(op)(app_data, test_data, **kwargs)

    def eq(self, variable, data):
        """Validate test data equality"""
        return self.data(variable, data)

    def dd(self, variable, data, **kwargs):
        """Validate test data equality"""
        return self.data(variable, data, op='dd', **kwargs)

    def ge(self, variable, data):
        """Validate test data equality"""
        return self.data(variable, data, op='ge')

    def gt(self, variable, data):
        """Validate test data equality"""
        return self.data(variable, data, op='gt')

    def jeq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='jeq', **kwargs)

    def json_eq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='jeq', **kwargs)

    def kveq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='kveq', **kwargs)

    def keyvalue_eq(self, variable, data, **kwargs):
        """Validate JSON data equality"""
        return self.data(variable, data, op='kveq', **kwargs)

    def lt(self, variable, data):
        """Validate test data less than"""
        return self.data(variable, data, op='lt')

    def le(self, variable, data):
        """Validate test data less than or equal"""
        return self.data(variable, data, op='le')

    def ne(self, variable, data):
        """Validate test data non equality"""
        return self.data(variable, data, op='ne')

    def rex(self, variable, data):
        """Test App data with regex"""
        return self.data(variable, data, op='rex')


class ThreatConnect(object):
    """Validate ThreatConnect data"""

    def __init__(self, provider):
        """Initialize class properties"""
        self.provider = provider

    def dir(self, directory, owner):
        """Validate the content of a given dir"""
        results = []
        for test_file in os.listdir(directory):
            if not (test_file.endswith('.json') and test_file.startswith('validate_')):
                continue
            results.append(self.file('{}/{}'.format(directory, test_file), owner))
        return results

    def file(self, file, owner):
        """Validate the content of a given file"""
        entities = self._convert_to_entities(file)
        return self.tc_entities(entities, owner)

    def tc_entities(self, tc_entities, owner, files=None):
        """Validate a array of tc_entities"""
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
        """Validate the ti_response entity"""
        parameters = {'includes': ['additional', 'attributes', 'labels', 'tags']}
        valid = True
        ti_entity = self._convert_to_ti_entity(tc_entity, owner)
        ti_response = ti_entity.single(params=parameters)
        if not self.success(ti_response):
            self.provider.log.error(
                'NotFoundError: Provided entity {} could not be fetched from ThreatConnect'.format(
                    tc_entity.get('summary')
                )
            )
            return False

        ti_response_entity = None
        ti_response = ti_response.json().get('data', {}).get(ti_entity.api_entity, {})
        for entity in self.provider.tcex.ti.entities(ti_response, tc_entity.get('type', None)):
            ti_response_entity = entity
            valid_attributes = self._response_attributes(ti_response, tc_entity)
            valid_tags = self._response_tags(ti_response, tc_entity)
            valid_labels = self._response_labels(ti_response, tc_entity)
            valid_file = self._file(ti_entity, file)
            if not valid_attributes or not valid_tags or not valid_labels or not valid_file:
                valid = False

        if ti_entity.type == 'Indicator':
            provided_rating = tc_entity.get('rating', None)
            expected_rating = ti_response.get('rating', None)
            if not provided_rating == expected_rating:
                self.provider.log.error(
                    'RatingError: Provided rating {} does not match '
                    'actual rating {}'.format(provided_rating, expected_rating)
                )
                valid = False

            provided_confidence = tc_entity.get('confidence', None)
            expected_confidence = ti_response.get('confidence', None)
            if not provided_confidence == expected_confidence:
                self.provider.log.error(
                    'ConfidenceError: Provided confidence {} does not match '
                    'actual confidence {}'.format(provided_confidence, expected_confidence)
                )
                valid = False
            provided_summary = ti_entity.unique_id
            expected_summary = ti_response_entity.get('value', None)
            if not provided_summary == expected_summary:
                self.provider.log.error(
                    'SummaryError: Provided summary {} does not match '
                    'actual summary {}'.format(provided_summary, expected_summary)
                )
                valid = False
        elif ti_entity.type == 'Group':
            provided_summary = tc_entity.get('summary', None)
            expected_summary = ti_response_entity.get('value', None)
            if not provided_summary == expected_summary:
                self.provider.log.error(
                    'SummaryError: Provided summary {} does not match '
                    'actual summary {}'.format(provided_summary, expected_summary)
                )
                valid = False
        return valid

    def flatten(self, lis):
        """Idk why python doesnt have this built in but helper function to flatten a list"""
        new_lis = []
        for item in lis:
            if isinstance(item, list):
                new_lis.extend(self.flatten(item))
            else:
                new_lis.append(item)
        return new_lis

    def compare_dicts(self, expected, actual, error_type=''):
        """Compare two dicts and returns a list of errors if they don't match"""
        valid = True
        for item in expected:
            if item in actual:
                if expected.get(item) == actual.get(item):
                    actual.pop(item)
                    continue
                self.provider.log.error(
                    '{0}{1} : {2} did not match {1} : {3}'.format(
                        error_type, item, expected.get('item'), actual.get(item)
                    )
                )
                valid = False
                actual.pop(item)
            else:
                self.provider.log.error(
                    '{}{} : {} was in expected results but not in actual results.'.format(
                        error_type, item, expected.get(item)
                    )
                )
                valid = False
        for item in actual.items():
            self.provider.log.error(
                '{}{} : {} was in actual results but not in expected results.'.format(
                    error_type, item, actual.get(item)
                )
            )
            valid = False

        return valid

    def compare_lists(self, expected, actual, error_type=''):
        """Compare two lists and returns a list of errors if they don't match"""
        valid = True
        for item in expected:
            if item in actual:
                actual.remove(item)
            else:
                self.provider.log.error(
                    '{}{} was in expected results but not in actual results.'.format(
                        error_type, item
                    )
                )
                valid = False
        for item in actual:
            self.provider.log.error(
                '{}{} was in actual results but not in expected results.'.format(error_type, item)
            )
            valid = False

        return valid

    @staticmethod
    def _convert_to_entities(file):
        """Convert file to tc_entity array"""
        with open(file, 'r') as read_file:
            data = json.load(read_file)
        return data

    def _convert_to_ti_entity(self, tc_entity, owner):
        """Convert a tc_entity to a ti_entity"""
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
        """Validate the ti_response attributes"""
        if not ti_response or not tc_entity:
            return True

        expected = {}
        actual = {}
        for attribute in tc_entity.get('attribute', []):
            expected[attribute.get('type')] = attribute.get('value')
        for attribute in ti_response.get('attribute', []):
            actual[attribute.get('type')] = attribute.get('value')
        valid = self.compare_dicts(expected, actual, error_type='AttributeError: ')

        return valid

    def _response_tags(self, ti_response, tc_entity):
        """Validate the ti_response tags"""
        if not ti_response or not tc_entity:
            return True

        expected = []
        actual = []
        for tag in tc_entity.get('tag', []):
            expected.append(tag)
        for tag in ti_response.get('tag', []):
            actual.append(tag.get('name'))
        valid = self.compare_lists(expected, actual, error_type='TagError: ')

        return valid

    def _response_labels(self, ti_response, tc_entity):
        """Validate the ti_response labels"""
        if not ti_response or not tc_entity:
            return True

        expected = []
        actual = []
        for tag in tc_entity.get('securityLabel', []):
            expected.append(tag)
        for tag in ti_response.get('securityLabel', []):
            actual.append(tag.get('name'))
        valid = self.compare_lists(expected, actual, error_type='SecurityLabelError: ')

        return valid

    def _file(self, ti_entity, file):
        """Handle file data"""
        valid = True
        if ti_entity.api_sub_type == 'Document' or ti_entity.api_sub_type == 'Report':
            actual_hash = ti_entity.get_file_hash()
            actual_hash = actual_hash.hexdigest()
            provided_hash = hashlib.sha256()
            with open(file, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    provided_hash.update(byte_block)
            provided_hash = provided_hash.hexdigest()
            if not provided_hash == actual_hash:
                self.provider.log.error(
                    'sha256 {} of provided file did not match sha256 of actual file {}'.format(
                        provided_hash, actual_hash
                    )
                )
                valid = False
        else:
            self.provider.log.error(
                'TypeError: {} entity type does not contain files.'.format(ti_entity.api_sub_type)
            )
            valid = False
        return valid

    @staticmethod
    def success(r):
        """???

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
