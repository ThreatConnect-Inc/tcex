# -*- coding: utf-8 -*-
"""TcEx Framework Playbook module"""
# standard library
import base64
import json
import re
from collections import OrderedDict


class PlaybooksBase:
    """TcEx Playbook Module Base Class

    Args:
        tcex (TcEx): Instance of TcEx class.
        context (str): The Redis context (hash).
        output_variables (list): The requested output variables.
    """

    def __init__(self, tcex, context, output_variables):
        """Initialize the Class properties."""
        self.tcex = tcex
        self._context = context
        self._output_variables = output_variables or []

        # properties
        self._key_value_store = None
        self._output_variables_by_name = None
        self._output_variables_by_type = None
        self.log = tcex.log

        # match full variable
        self._variable_match = re.compile(fr'^{self._variable_pattern}$')
        # capture variable parts (exactly a variable)
        self._variable_parse = re.compile(self._variable_pattern)
        # match embedded variables without quotes (#App:7979:variable_name!StringArray)
        self._vars_keyvalue_embedded = re.compile(fr'(?:\"\:\s?)[^\"]?{self._variable_pattern}')

    def _coerce_string_value(self, value):
        """Return a string value from an bool or int."""
        # coerce bool before int as python says a bool is an int
        if isinstance(value, bool):
            # coerce bool to str type
            self.log.warning(f'Coercing bool value ({value}) to a string ("{str(value).lower()}").')
            value = str(value).lower()

        # coerce int to str type
        if isinstance(value, (float, int)):
            self.log.warning(f'Coercing float/int value ({value}) to a string ("{str(value)}").')
            value = str(value)

        return value

    def _create(self, key, value, validate=True):
        """Create the value in Redis if applicable."""
        if key is None or value is None:
            self.log.warning('The key or value field is None.')
            return None

        # get variable type from variable value
        variable_type = self.variable_type(key)

        if variable_type == 'Binary':
            # if not isinstance(value, bytes):
            #     value = value.encode('utf-8')
            if validate and not isinstance(value, bytes):
                raise RuntimeError('Invalid data provided for Binary.')
            value = base64.b64encode(value).decode('utf-8')
        elif variable_type == 'KeyValue':
            if validate and (not isinstance(value, dict) or not self._is_key_value(value)):
                raise RuntimeError('Invalid data provided for KeyValue.')
        elif variable_type == 'String':
            # coerce string values
            value = self._coerce_string_value(value)

            if validate and not isinstance(value, str):
                raise RuntimeError('Invalid data provided for String.')
        elif variable_type == 'TCEntity':
            if validate and (not isinstance(value, dict) or not self._is_tc_entity(value)):
                raise RuntimeError('Invalid data provided for TcEntity.')

        # self.log.trace(f'pb create - context: {self._context}, key: {key}, value: {value}')
        try:
            value = json.dumps(value)
        except ValueError as e:  # pragma: no cover
            raise RuntimeError(f'Failed to serialize value ({e}).')

        return self.key_value_store.create(key.strip(), value)

    def _create_array(self, key, value, validate=True):
        """Create the value in Redis if applicable."""
        if key is None or value is None:
            self.log.warning('The key or value field is None.')
            return None

        # get variable type from variable value
        variable_type = self.variable_type(key)

        if variable_type == 'BinaryArray':
            if validate and not isinstance(value, list):
                raise RuntimeError('Invalid data provided for BinaryArray.')

            value_encoded = []
            for v in value:
                if v is not None:
                    if validate and not isinstance(v, bytes):
                        raise RuntimeError('Invalid data provided for Binary.')
                    # if not isinstance(v, bytes):
                    #     v = v.encode('utf-8')
                    v = base64.b64encode(v).decode('utf-8')
                value_encoded.append(v)
            value = value_encoded
        elif variable_type == 'KeyValueArray':
            if validate and (not isinstance(value, list) or not self._is_key_value_array(value)):
                raise RuntimeError('Invalid data provided for KeyValueArray.')
        elif variable_type == 'StringArray':
            if validate and not isinstance(value, list):
                raise RuntimeError('Invalid data provided for StringArray.')

            value_coerced = []
            for v in value:
                # coerce string values
                v = self._coerce_string_value(v)

                if validate and not isinstance(v, (type(None), str)):
                    raise RuntimeError('Invalid data provided for StringArray.')
                value_coerced.append(v)
            value = value_coerced
        elif variable_type == 'TCEntityArray':
            if validate and (not isinstance(value, list) or not self._is_tc_entity_array(value)):
                raise RuntimeError('Invalid data provided for TcEntityArray.')

        # self.log.trace(f'pb create - context: {self._context}, key: {key}, value: {value}')
        try:
            value = json.dumps(value)
        except ValueError as e:  # pragma: no cover
            raise RuntimeError(f'Failed to serialize value ({e}).')

        return self.key_value_store.create(key.strip(), value)

    @staticmethod
    def _decode_binary(data):
        """Return decoded bytes data handling data written by java apps."""
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:  # pragma: no cover
            # for data written an upstream java App
            data = data.decode('latin-1')
        return data

    @staticmethod
    def _is_key_value(data):
        """Return True if provided data has proper structure for Key Value."""
        return all(x in data for x in ['key', 'value'])

    def _is_key_value_array(self, data):
        """Return True if provided data has proper structure for Key Value Array."""
        for d in data:
            if not self._is_key_value(d):
                return False
        return True

    @staticmethod
    def _is_tc_entity(data):
        """Return True if provided data has proper structure for TC Entity."""
        return all(x in data for x in ['id', 'value', 'type'])

    def _is_tc_entity_array(self, data):
        """Return True if provided data has proper structure for TC Entity Array."""
        for d in data:
            if not self._is_tc_entity(d):
                return False
        return True

    @staticmethod
    def _load_value(value):
        """Return the loaded JSON value or raise an error.

        Args:
            value (str): The data from key/value store.

        Raises:
            RuntimeError: Raise error when data can't be loaded as JSON data.

        Returns:
            any: The de-serialized value from the key/value store.
        """
        try:
            return json.loads(value, object_pairs_hook=OrderedDict)
        except ValueError as e:  # pragma: no cover
            raise RuntimeError(f'Failed to JSON load data "{value}" ({e}).')

    def _parse_output_variables(self):
        """Parse the output variables provided to Playbook Class.

        **Example Variable Format**::

            ['#App:1234:status!String', '#App:1234:status_code!String']
        """
        self._output_variables_by_name = {}
        self._output_variables_by_type = {}
        for ov in self._output_variables:
            # parse the variable to get individual parts
            parsed_variable = self.parse_variable(ov)
            variable_name = parsed_variable.get('name')
            variable_type = parsed_variable.get('type')

            # store the variables in dict by name (e.g. "status_code")
            self._output_variables_by_name[variable_name] = {'variable': ov}

            # store the variables in dict by name-type (e.g. "status_code-String")
            self._output_variables_by_type[f'{variable_name}-{variable_type}'] = {'variable': ov}

    def _read(self, key, embedded=True, b64decode=True, decode=False):
        """Create the value in Redis if applicable."""
        if key is None:
            self.log.warning('The key is None.')
            return None

        # get variable type from variable value
        variable_type = self.variable_type(key)

        value = self.key_value_store.read(key.strip())
        if value is None:
            return value

        if variable_type == 'Binary':
            value = self._load_value(value)

            if b64decode:
                value = base64.b64decode(value)
                if decode:
                    value = self._decode_binary(value)
        elif variable_type == 'KeyValue':
            # embedded variable can be unquoted, which breaks JSON.
            value = self._wrap_embedded_keyvalue(value)

            if embedded:
                value = self._read_embedded(value)

            value = self._load_value(value)
        elif variable_type == 'String':
            if embedded:
                value = self._read_embedded(value)

            # coerce string values
            value = self._coerce_string_value(self._load_value(value))
        elif variable_type == 'TCEntity':
            value = self._load_value(value)

        return value

    def _read_array(self, key, embedded=True, b64decode=True, decode=False):
        """Create the value in Redis if applicable."""
        if key is None:  # pragma: no cover
            self.log.warning('The null value for key was provided.')
            return None

        # get variable type from variable value
        variable_type = self.variable_type(key)

        value = self.key_value_store.read(key.strip())
        if value is None:
            return value

        if variable_type == 'BinaryArray':
            value = json.loads(value, object_pairs_hook=OrderedDict)

            values = []
            for v in value:
                if v is not None and b64decode:
                    v = base64.b64decode(v)
                    if decode:
                        v = self._decode_binary(v)
                values.append(v)
            value = values
        elif variable_type == 'KeyValueArray':
            # embedded variable can be unquoted, which breaks JSON.
            value = self._wrap_embedded_keyvalue(value)

            if embedded:
                value = self._read_embedded(value)

            try:
                value = json.loads(value, object_pairs_hook=OrderedDict)
            except ValueError as e:  # pragma: no cover
                raise RuntimeError(f'Failed loading JSON data ({value}). Error: ({e})')
        elif variable_type == 'StringArray':
            if embedded:
                value = self._read_embedded(value)

            # convert int to str
            value_coerced = []
            for v in self._load_value(value):
                # coerce string values
                value_coerced.append(self._coerce_string_value(v))
            value = value_coerced
        elif variable_type in ['TCEntityArray', 'TCEnhancedEntity', 'TCEnhancedEntityArray']:
            value = self._load_value(value)

        # self.log.trace(f'pb create - context: {self._context}, key: {key}, value: {value}')
        return value

    def _read_embedded(self, value):
        """Read method for "embedded" variables.

        .. Note:: The ``read()`` method will automatically determine if the input is a variable or
            needs to be searched for embedded variables.

        Embedded variable rules:

        * Only user input can have embedded variables.
        * Only String and KeyValueArray variables can have embedded variables.
        * Variables can only be embedded one level deep.

        This method will automatically covert variables embedded in a string with value retrieved
        from DB. If there are no keys/variables the raw string will be returned.

        Examples::

            DB Values
            #App:7979:variable_name!String:
                "embedded \\"variable\\""
            #App:7979:two!String:
                "two"
            #App:7979:variable_name!StringArray:
                ["one", "two", "three"]

            Examples 1:
                Input:  "This input has a embedded #App:7979:variable_name!String"

            Examples 2:
                Input: ["one", #App:7979:two!String, "three"]

            Examples 3:
                Input: [{
                    "key": "embedded string",
                    "value": "This input has a embedded #App:7979:variable_name!String"
                }, {
                    "key": "string array",
                    "value": #App:7979:variable_name!StringArray
                }, {
                    "key": "string",
                    "value": #App:7979:variable_name!String
                }]

        Args:
            value (str): The value to parsed and updated from the DB.
            parent_var_type (str): The parent type of the embedded variable.

        Returns:
            (str): Results retrieved from DB
        """
        if value is None:  # pragma: no cover
            return value

        for variable in (v.group(0) for v in re.finditer(self._variable_parse, str(value))):
            v = self.read(variable)
            self.log.trace(f'embedded variable: {variable}, value: {v}')
            if isinstance(v, (dict, list)):
                v = json.dumps(v)
                # for KeyValueArray with nested dict/list type replace the
                # quoted value to ensure the resulting data is loadable JSON
                value = re.sub(f'"{variable}"', v, value)

            if v is not None:
                # only replace variable if a non-null value is returned from kv store
                value = re.sub(variable, v, value)
        return value

    @property
    def _variable_pattern(self):
        """Regex pattern to match and parse a playbook variable."""
        variable_pattern = r'#([A-Za-z]+)'  # match literal (#App,#Trigger) at beginning of String
        variable_pattern += r':([\d]+)'  # app id (:7979)
        variable_pattern += r':([A-Za-z0-9_\.\-\[\]]+)'  # variable name (:variable_name)
        variable_pattern += r'!(StringArray|BinaryArray|KeyValueArray'  # variable type (array)
        variable_pattern += r'|TCEntityArray|TCEnhancedEntityArray'  # variable type (array)
        variable_pattern += r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'  # variable type
        variable_pattern += r'|(?:(?!String)(?!Binary)(?!KeyValue)'  # non matching for custom
        variable_pattern += r'(?!TCEntity)(?!TCEnhancedEntity)'  # non matching for custom
        variable_pattern += r'[A-Za-z0-9_-]+))'  # variable type (custom)
        return variable_pattern

    @property
    def _variable_array_types(self):
        """Return list of standard playbook array variable types."""
        return [
            'BinaryArray',
            'KeyValueArray',
            'StringArray',
            'TCEntityArray',
            'TCEnhancedEntityArray',
        ]

    @property
    def _variable_single_types(self):
        """Return list of standard playbook single variable types."""
        return [
            'Binary',
            'KeyValue',
            'String',
            'TCEntity',
            'TCEnhancedEntity',
        ]

    @property
    def _variable_types(self):
        """Return list of standard playbook variable typesd."""
        return self._variable_single_types + self._variable_array_types

    def _wrap_embedded_keyvalue(self, data):
        """Wrap keyvalue embedded variable in double quotes.

        Args:
            data (str): The data with embedded variables.

        Returns:
            (str): Results retrieved from DB
        """
        # TODO: need to verify if core still sends improper JSON for KeyValueArrays
        if data is not None:  # pragma: no cover
            variables = []
            for v in re.finditer(self._vars_keyvalue_embedded, data):
                variables.append(v.group(0))

            for var in set(variables):  # recursion over set to handle duplicates
                # pull (#App:1441:embedded_string!String) from (": #App:1441:embedded_string!String)
                variable_string = re.search(self._variable_parse, var).group(0)
                # reformat to replace the correct instance only, handling the case where a variable
                # is embedded multiple times in the same key value array.
                data = data.replace(var, f'": "{variable_string}"')
        return data

    @property
    def key_value_store(self):
        """Return the correct KV store for this execution."""
        if self._key_value_store is None:
            if self.tcex.default_args.tc_playbook_db_type == 'Redis':
                from ..key_value_store import KeyValueRedis

                self._key_value_store = KeyValueRedis(self._context, self.tcex.redis_client)
            elif self.tcex.default_args.tc_playbook_db_type == 'TCKeyValueAPI':
                from ..key_value_store import KeyValueApi

                self._key_value_store = KeyValueApi(self.tcex.session)
            else:  # pragma: no cover
                raise RuntimeError(
                    f'Invalid DB Type: ({self.tcex.default_args.tc_playbook_db_type})'
                )
        return self._key_value_store

    def create_raw(self, key, value):
        """Create method of CRUD operation for raw data.

        ..important:: Raw data can only be a byte, str or int. Other data structures
            (dict, list, etc) must be serialized.

        Args:
            key (str): The variable to write to the DB.
            value (bytes|int|string): The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        data = None
        if key is not None and value is not None:
            data = self.key_value_store.create(key.strip(), value)
        else:
            self.log.warning('The key or value field was None.')
        return data

    def read_raw(self, key):
        """Read method of CRUD operation for raw data.

        ..important:: Bytes input will be returned a as string as there is
            no way to determine data from redis originated as bytes or string.

        Args:
            key (str): The variable to read from the DB.

        Returns:
            (str): Results retrieved from DB.
        """
        value = None
        if key is not None:
            value = self.key_value_store.read(key.strip())
        else:
            self.log.warning('The key field was None.')
        return value

    def parse_variable(self, variable):  # pragma: no cover
        """Set placeholder for child method."""
        raise NotImplementedError('Implemented in child class')

    def read(self, key, array=False, embedded=True):  # pragma: no cover
        """Set placeholder for child method."""
        raise NotImplementedError('Implemented in child class')

    def variable_type(self, variable):  # pragma: no cover
        """Set placeholder for child method."""
        raise NotImplementedError('Implemented in child class')
