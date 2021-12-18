"""TcEx Framework Playbook module"""
# standard library
import re
from typing import Any, List, Optional, Union

# first-party
from tcex.key_value_store import KeyValueApi, KeyValueRedis
from tcex.playbook.playbook_read_abc import PlaybookReadABC
from tcex.playbook.playbook_write_abc import PlaybookWriteABC


class Playbook(PlaybookReadABC, PlaybookWriteABC):
    """Playbook methods for accessing key value store.

    Args:
        key_value_store: A KV store instance.
        context: The KV Store context/session_id. For PB Apps the context is provided on
            startup, but for service Apps each request gets a different context.
        output_variables: The requested output variables. For PB Apps outputs are provided on
            startup, but for service Apps each request gets different outputs.
    """

    def __init__(
        self,
        key_value_store: Union[KeyValueApi, KeyValueRedis],
        context: Optional[str] = None,
        output_variables: Optional[list] = None,
    ) -> None:
        """Initialize the class properties."""
        super().__init__(key_value_store, context, output_variables)

        # properties
        self.output_data = {}

    def add_output(
        self, key: str, value: Any, variable_type: str, append_array: Optional[bool] = True
    ) -> None:
        """Dynamically add output to output_data dictionary to be written to DB later.

        This method provides an alternative and more dynamic way to create output variables in an
        App. Instead of storing the output data manually and writing all at once the data can be
        stored inline, when it is generated and then written before the App completes.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            colors = ['blue', 'red', 'yellow']:
            tcex.playbook.add_output('app.colors', colors, 'StringArray')

            tcex.playbook.write_output()  #  writes the output stored in output_data

        .. code-block:: json
            :linenos:
            :lineno-start: 1

            {
                "my_color-String": {
                    "key": "my_color",
                    "type": "String",
                    "value": "blue"
                },
                "my_numbers-String": {
                    "key": "my_numbers",
                    "type": "String",
                    "value": "seven"
                },
                "my_numbers-StringArray": {
                    "key": "my_numbers",
                    "type": "StringArray",
                    "value": ["seven", "five"]
                }
            }

        Args:
            key: The variable name to write to storage.
            value: The value to write to storage.
            variable_type: The variable type being written.
            append_array: If True arrays will be appended instead of being overwritten.
        """
        index = f'{key}-{variable_type}'
        self.output_data.setdefault(index, {})
        if value is None:
            if variable_type not in self._variable_array_types:
                # never append or store None values if not an array
                return
            if not append_array and variable_type in self._variable_array_types:
                # Only store none for array types when append is True
                return

        if variable_type in self._variable_array_types and append_array:
            self.output_data[index].setdefault('key', key)
            self.output_data[index].setdefault('type', variable_type)
            if isinstance(value, list):
                self.output_data[index].setdefault('value', []).extend(value)
            else:
                self.output_data[index].setdefault('value', []).append(value)
        else:
            self.output_data[index] = {'key': key, 'type': variable_type, 'value': value}

    def check_output_variable(self, variable: str) -> bool:
        """Return True if output variable was requested by downstream app.

        Using the auto generated dictionary of output variables check to see if provided
        variable was requested by downstream app.
        """
        return variable in self.output_variables_by_key

    def create(self, key: str, value: Any) -> str:
        """Create method of CRUD operation for working with KeyValue DB.

        This method will automatically determine the variable type and
        call the appropriate method to write the data.  If a non standard
        type is provided the data will be written as RAW data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result string of DB write.
        """
        data = None
        if key is not None:
            key = key.strip()
            parsed_key = self.parse_variable(key.strip())
            variable_type = parsed_key['type']

            # log/debug
            self.log.debug(f'create variable {key}')
            if variable_type not in ['Binary', 'BinaryArray']:
                self.log.trace(f'variable value: {value}')

            if variable_type in self._variable_single_types:
                data = self._create(key, value)
            elif variable_type in self._variable_array_types:
                data = self._create_array(key, value)
            else:
                data = self.create_raw(key, value)
        return data

    def create_binary(self, key: str, value: bytes) -> str:
        """Create method of CRUD operation for binary data.

        Args:
            key: The variable to write to the Key Value Store.
            value: The data to write to the Key Value Store.

        Returns:
            (str): Result of Key Value Store write.
        """
        supported_variable_type = 'Binary'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_binary_array(self, key: str, value: List[bytes]) -> str:
        """Create method of CRUD operation for binary array data.

        Args:
            key: The variable to write to the Key Value Store.
            value: The data to write to the Key Value Store.

        Returns:
            (str): Result of Key Value Store write.
        """
        supported_variable_type = 'BinaryArray'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_key_value(self, key: str, value: Any) -> str:
        """Create method of CRUD operation for key/value data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write
        """
        supported_variable_type = 'KeyValue'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_key_value_array(self, key: str, value: List[Any]) -> str:
        """Create method of CRUD operation for key/value array data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'KeyValueArray'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_string(self, key: str, value: str) -> str:
        """Create method of CRUD operation for string data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'String'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_string_array(self, key: str, value: List[str]) -> str:
        """Create method of CRUD operation for string array data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'StringArray'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_tc_entity(self, key: str, value: dict) -> str:
        """Create method of CRUD operation for TC entity data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = 'TCEntity'
        if self.variable_type(key) != supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create(key, value)

    def create_tc_entity_array(self, key: str, value: List[dict]) -> str:
        """Create method of CRUD operation for TC entity array data.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        supported_variable_type = ['TCEntityArray', 'TCEnhancedEntity', 'TCEnhancedEntityArray']
        if self.variable_type(key) not in supported_variable_type:
            raise RuntimeError(f'The key provided ({key}) is not a {supported_variable_type} key.')
        return self._create_array(key, value)

    def create_output(self, key: str, value: Any, variable_type: Optional[str] = None) -> str:
        """Alias for Create method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if provided variable was requested by
        a downstream app and if so create the data in the KeyValue DB.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.
            variable_type: The variable type being written.

        Returns:
            (str): Result string of DB write.
        """
        #  This is if no downstream variables are requested then nothing should be returned.
        if not self.output_variables_by_type:  # pragma: no cover
            self.log.debug(f'Variable {key} was NOT requested by downstream app.')
            return None

        if key is None:
            self.log.info('Key has a none value and will not be written.')
            return None

        if value is None:
            self.log.info(f'Variable {key} has a none value and will not be written.')
            return None

        key = key.strip()
        key_type = f'{key}-{variable_type}'
        results = None
        if self.output_variables_by_type.get(key_type) is not None:
            # variable key-type has been requested
            v = self.output_variables_by_type.get(key_type)
            self.log.info(f"Variable {v.get('variable')} was requested by downstream App.")
            results = self.create(v.get('variable'), value)
        elif self.output_variables_by_key.get(key) is not None and variable_type is None:
            # variable key has been requested
            v = self.output_variables_by_key.get(key)
            self.log.info(f"Variable {v.get('variable')} was requested by downstream App.")
            results = self.create(v.get('variable'), value)
        else:
            self.log.trace(f'requested output variables: {self.output_variables_by_key}')
            self.log.debug(f'Variable {key} was NOT requested by downstream app.')

        return results

    def delete(self, key: str) -> str:
        """Delete method of CRUD operation for all data types.

        This method is only supported when using key_value_redis.

        Args:
            key: The variable to write to the DB.

        Returns:
            (str): Result of DB write.
        """
        data = None
        if key is not None:
            data = self.key_value_store.delete(self._context, key.strip())
        else:  # pragma: no cover
            self.log.warning('The key field was None.')
        return data

    def is_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted playbook variable."""
        return self.utils.is_playbook_variable(key)

    @property
    def output_variables_by_key(self) -> dict:
        """Return output variables stored as name dict."""
        if self._output_variables_by_key is None:
            self._parse_output_variables()
        return self._output_variables_by_key

    @property
    def output_variables_by_type(self) -> dict:
        """Return output variables stored as name-type dict."""
        if self._output_variables_by_type is None:
            self._parse_output_variables()
        return self._output_variables_by_type

    def parse_variable(self, variable: str) -> dict:
        """Parse an input or output variable.

        **Example Variable**::

        #App:1234:output!String

        Args:
            variable: The variable name to parse.

        Returns:
            (dict): Result of parsed string.
        """
        data = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self.utils.variable_playbook_match, variable):
                var = re.search(self.utils.variable_playbook_parse, variable)
                data = {
                    'app_type': var.group('app_type'),
                    'job_id': var.group('job_id'),
                    'key': var.group('key'),
                    'type': var.group('type'),
                }
        return data

    def read(
        self, key: str, array: Optional[bool] = False
    ) -> Optional[Union[bytes, dict, list, str]]:
        """Read method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if a single variable is passed
        or if "mixed" data is passed and return the results from the DB. It will also
        automatically determine the variable type to read.
        """
        value = key
        if isinstance(key, str):
            key = key.strip()
            variable_type = self.variable_type(key)

            if re.match(self.utils.variable_playbook_match, key):
                # only log key if it's a variable
                self.log.debug(f'read variable {key}')

                if variable_type in self._variable_types:
                    value = self.read_any(key=key)
                else:
                    value = self.read_raw(key)
            else:
                if variable_type == 'String':
                    value = self._process_space_patterns(value)

        if array is True:
            value = self._to_array(value)

        return value

    def read_any(self, key: str) -> Optional[Union[bytes, dict, list, str]]:
        """Return the value from the keystore for all types.

        This is a quick helper method, for more advanced features
        the individual read methods should be used (e.g., read_binary).
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        variable_type = self.variable_type(key).lower()
        variable_type_map = {
            'binary': self.read_binary,
            'binaryarray': self.read_binary_array,
            'keyvalue': self.read_key_value,
            'keyvaluearray': self.read_key_value_array,
            'string': self.read_string,
            'stringarray': self.read_string_array,
            'tcentity': self.read_tc_entity,
            'tcentityarray': self.read_tc_entity_array,
            'tcenhancedentity': self.read_tc_entity,
        }
        return variable_type_map.get(variable_type)(key)

    def read_binary(
        self,
        key: str,
        b64decode: Optional[bool] = True,
        decode: Optional[bool] = False,
    ) -> Optional[Union[str, bytes]]:
        """Read the value from key value store.

        Binary data should be stored as base64 encoded string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        return self._process_binary(data, b64decode=b64decode, decode=decode, serialized=True)

    def read_binary_array(
        self,
        key: str,
        b64decode: Optional[bool] = True,
        decode: Optional[bool] = False,
    ) -> Optional[List[Union[bytes, str]]]:
        """Read the value from key value store.

        BinaryArray data should be stored as base64 encoded serialized string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        if data is not None:
            # data should be base64 encoded bytes string

            # decode the entire response, but not the items in the array?
            data = data.decode()

            # Array type is serialized before writing to redis, deserialize the data
            data = self._load_data(data)

            values = []
            for d in data:
                # d should be a base64 encoded string
                values.append(
                    self._process_binary(d, b64decode=b64decode, decode=decode, serialized=False)
                )
            data = values

        return data

    def read_key_value(
        self,
        key: str,
        resolve_embedded: Optional[bool] = True,
    ) -> Optional[dict]:
        """Read the value from key value store.

        KeyValue data should be stored as a JSON string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        return self._process_key_value(data, resolve_embedded=resolve_embedded, serialized=True)

    def read_key_value_array(
        self,
        key: str,
        resolve_embedded: Optional[bool] = True,
    ) -> Optional[List[str]]:
        """Read the value from key value store.

        KeyValueArray data should be stored as serialized string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        if data is not None:
            # data should be string

            # decode the entire response, but not the items in the array?
            data = data.decode()

            # Array type is serialized before writing to redis, deserialize the data
            data = self._load_data(data)

            values = []
            for d in data:
                # d should be a base64 encoded string
                values.append(
                    self._process_key_value(d, resolve_embedded=resolve_embedded, serialized=False)
                )
            data = values

        return data

    def read_string(
        self,
        key: str,
        resolve_embedded: Optional[bool] = True,
    ) -> Optional[str]:
        """Read the value from key value store.

        String data should be stored as serialized string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        return self._process_string(data, resolve_embedded=resolve_embedded, serialized=True)

    def read_string_array(
        self,
        key: str,
        resolve_embedded: Optional[bool] = True,
    ) -> Optional[List[str]]:
        """Read the value from key value store.

        StringArray data should be stored as serialized string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        if data is not None:
            # data should be string

            # decode the entire response, but not the items in the array?
            data = data.decode()

            # Array type is serialized before writing to redis, deserialize the data
            data = self._load_data(data)

            values = []
            for d in data:
                # d should be a base64 encoded string
                values.append(
                    self._process_string(d, resolve_embedded=resolve_embedded, serialized=False)
                )
            data = values

        return data

    def read_tc_entity(self, key: str) -> Optional[dict]:
        """Read the value from key value store.

        TCEntity data should be stored as serialized string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        return self._process_tc_entity(data, serialized=True)

    def read_tc_entity_array(
        self,
        key: str,
    ) -> Optional[List[str]]:
        """Read the value from key value store.

        TCEntityArray data should be stored as serialized string.
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        data: Optional[str] = self._get_data(key)
        if data is not None:
            # data should be string

            # decode the entire response, but not the items in the array?
            data = data.decode()

            # Array type is serialized before writing to redis, deserialize the data
            data = self._load_data(data)

            values = []
            for d in data:
                # d should be a base64 encoded string
                values.append(self._process_tc_entity(d, serialized=False))
            data = values

        return data

    def variable_type(self, variable: str) -> str:
        """Get the Type from the variable string or default to String type.

        The default type is "String" for those cases when the input variable is
        contains not "DB variable" and is just a String.

        Example Variable:

        #App:1234:output!StringArray returns **StringArray**

        Example String:

        "My Data" returns **String**
        """
        return self.utils.get_playbook_variable_type(variable)

    def write_output(self):
        """Write all stored output data to storage."""
        for data in self.output_data.values():
            self.create_output(data.get('key'), data.get('value'), data.get('type'))
