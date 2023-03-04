"""Playbook ABC"""
# standard library
import base64
import json
import logging
import re
from collections import OrderedDict
from typing import Any

# first-party
from tcex.key_value_store.key_value_abc import KeyValueABC
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module
from tcex.pleb.registry import registry
from tcex.utils.utils import Utils
from tcex.utils.variables import BinaryVariable, StringVariable

# get tcex logger
logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


class PlaybookRead:
    """Playbook Read

    Args:
        key_value_store: A KV store instance.
        context: The KV Store context/session_id. For PB Apps the context is provided on
            startup, but for service Apps each request gets a different context.
        output_variables: The requested output variables. For PB Apps outputs are provided on
            startup, but for service Apps each request gets different outputs.
    """

    def __init__(self, context: str, key_value_store: KeyValueABC):
        """Initialize the class properties."""
        self.context = context
        self.key_value_store = key_value_store

        # properties
        self.log = logger
        self.utils = Utils()

    def _check_variable_type(self, variable: str, type_: str):
        """Validate the correct type was passed to the method."""
        if self.utils.get_playbook_variable_type(variable).lower() != type_.lower():
            raise RuntimeError(
                f'Invalid variable provided ({variable}), variable must be of type {type_}.'
            )

    @staticmethod
    def _coerce_string_value(value: bool | float | int | str) -> str:
        """Return a string value from an bool or int."""
        # coerce bool before int as python says a bool is an int
        if isinstance(value, bool):
            # coerce bool to str type
            value = str(value).lower()

        # coerce int to str type
        if isinstance(value, (float, int)):
            value = str(value)

        return value

    @staticmethod
    def _decode_binary(data: bytes) -> str:
        """Return decoded bytes data handling data written by java apps."""
        try:
            _data = data.decode('utf-8')
        except UnicodeDecodeError:  # pragma: no cover
            # for data written an upstream java App
            _data = data.decode('latin-1')
        return _data

    @staticmethod
    def _deserialize_data(value: bytes | str) -> Any:
        """Return the loaded JSON value or raise an error."""
        try:
            return json.loads(value, object_pairs_hook=OrderedDict)
        except ValueError as e:  # pragma: no cover
            raise RuntimeError(f'Failed to JSON load data "{value}" ({e}).')

    def _get_data(self, key: str) -> bytes | str | None:
        """Get the value from Redis if applicable."""
        try:
            return self.key_value_store.read(self.context, key.strip())
        except RuntimeError as e:
            self.log.error(e)
        return None

    @staticmethod
    def _load_data(value: str) -> dict | list[dict | str] | str:
        """Return the loaded JSON value or raise an error."""
        try:
            return json.loads(value, object_pairs_hook=OrderedDict)
        except ValueError as e:  # pragma: no cover
            raise RuntimeError(f'Failed to JSON load data "{value}" ({e}).')

    def _null_key_check(self, key: Any) -> bool:
        """Return False if value is not null."""
        if key is None:
            self.log.warning('The provided key was None.')
            return True

        return False

    def _process_key_value(self, data: dict, resolve_embedded: bool) -> dict | None:
        """Read the value from key value store.

        KeyValue data should be stored as a JSON string.
        """
        # IMPORTANT:
        # A Single level of nested variables is supported. There is no way
        # in the TC platform to create double nested variables. Any App
        # that would try and create a double nested variable is improperly
        # written.

        # KeyValue List Input
        # -------------------------------------------------------------
        # | key                         | value                       |
        # =============================================================
        # | my_binary                   | #App:7979:two!Binary        |
        # -------------------------------------------------------------
        # | my_binary_array             | #App:7979:two!BinaryArray   |
        # -------------------------------------------------------------
        # | my_key_value                | #App:7979:two!KeyValue      |
        # -------------------------------------------------------------
        # | my_key_value_array          | #App:7979:two!KeyValueArray |
        # -------------------------------------------------------------
        # | my_string                   | #App:7979:two!String        |
        # -------------------------------------------------------------
        # | my_string_array             | #App:7979:two!StringArray   |
        # -------------------------------------------------------------
        # | my_tcentity                 | #App:7979:two!TCEntity      |
        # -------------------------------------------------------------
        # | my_tcentity_array           | #App:7979:two!TCEntityArray |
        # -------------------------------------------------------------

        # An upstream Apps KeyValue output can be used in a KeyValueList input, but
        # Apps SHOULD NOT be writing KeyValueArray with nested variables. This means
        # that there will only ever be 1 levels of nesting.

        # KeyValueList Input -> Nested KeyValue/KeyValueArray, the nested
        # KeyValue/KeyValueArray CAN NOT have nested variables since they
        # have to come from an upstream App.

        # check if keyvalue value is a variable
        if resolve_embedded:
            value = data['value']
            if self.utils.is_playbook_variable(value):
                # any type can be nested, but no further nesting is supported
                data['value'] = self.any(value)
            else:
                # read embedded is less efficient and has more caveats
                data['value'] = self._read_embedded(value)

        return data

    @staticmethod
    def _process_space_patterns(string: str) -> str:
        r"""Return the string with \s replace with spaces."""
        # replace "\s" with a space only for user input.
        # using '\\s' will prevent replacement.
        string = re.sub(r'(?<!\\)\\s', ' ', string)
        string = re.sub(r'\\\\s', r'\\s', string)
        return string

    def _read_embedded(self, value: str) -> str:
        """Read method for "embedded" variables.

        .. Note:: The ``read()`` method will automatically determine if the input is a variable or
            needs to be searched for embedded variables.

        Embedded variable rules:

        * Only user input can have embedded variables.
        * Only String and KeyValueArray variables can have embedded variables.
        * Variables can only be embedded one level deep.

        This method will automatically convert variables embedded in a string with value retrieved
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

        Returns:
            (str): Results retrieved from DB
        """
        if value is None:  # pragma: no cover
            return value

        for match in re.finditer(self.utils.variable_expansion_pattern, str(value)):
            variable = match.group(0)  # the full variable pattern
            v = None
            if match.group('origin') == '#':  # pb-variable
                v = self.any(variable)
            elif match.group('origin') == '&':  # tc-variable
                v = registry.resolve_variable(variable)

            # TODO: [high] should this behavior be changed in 3.0?
            self.log.trace(f'embedded variable: {variable}, value: {v}')

            if match.group('type') in ['Binary', 'BinaryArray']:
                self.log.trace(
                    f'Binary types may not be embedded into strings. Could not embed: {variable}'
                )
                v = '<binary>'

            if isinstance(v, (dict, list)):
                v = json.dumps(v)
            elif v is None:
                v = '<null>'

            # value.replace was chosen over re.sub due to an issue encountered while testing an app.
            # re.sub will handle escaped characters like \t, value.replace would not handle these
            # scenarios.
            if isinstance(v, str):
                value = value.replace(variable, v)

        return StringVariable(value)

    @staticmethod
    def _to_array(value: list | str | None) -> list:
        """Return the provided array as a list."""
        if value is None:
            # Adding none value to list breaks App logic. It's better to not request
            # Array and build array externally if None values are required.
            value = []
        elif not isinstance(value, list):
            value = [value]
        return value

    def any(self, key: str) -> bytes | dict | list | str | None:
        """Return the value from the keystore for all types.

        This is a quick helper method, for more advanced features
        the individual read methods should be used (e.g., binary).
        """
        if self._null_key_check(key) is True:
            return None

        key = key.strip()  # clean up key
        variable_type = self.utils.get_playbook_variable_type(key).lower()
        variable_type_map = {
            'binary': self.binary,
            'binaryarray': self.binary_array,
            'keyvalue': self.key_value,
            'keyvaluearray': self.key_value_array,
            'string': self.string,
            'stringarray': self.string_array,
            'tcbatch': self.tc_batch,
            'tcentity': self.tc_entity,
            'tcentityarray': self.tc_entity_array,
            # 'tcenhancedentity': self.tc_entity,
        }
        value = variable_type_map.get(variable_type, self.raw)(key)

        if value is not None:
            if variable_type == 'binary':
                value = BinaryVariable(value)
            elif variable_type == 'binaryarray':
                value = [v if v is None else BinaryVariable(v) for v in value]
            elif variable_type == 'string':
                value = StringVariable(value)
            elif variable_type == 'stringarray':
                value = [v if v is None else StringVariable(v) for v in value]

        return value

    def binary(
        self,
        key: str,
        b64decode: bool = True,
        decode: bool = False,
    ) -> BinaryVariable | str | None:
        """Read the value from key value store.

        The binary write method base64 encodes the data, then decodes the bytes to string, and
        finally serializes the string before writing to the key value store.

        This method will deserialize the string, then OPTIONALLY base64 decode the data, and
        finally return the Binary data.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'Binary')

        # get the data from the key value store
        data = self._get_data(key)
        if data is None:
            return None

        # reverse the order of the binary create/write method
        # 1. deserialize the data
        # 2. base64 decode the data

        # deserialize the data
        data = self._deserialize_data(data)

        # base64 decode the data (get_data returns multiple types, but the binary
        # write method will always write a base64.encoded->bytes.decoded->serialized string)
        # for the testing framework, the base64 encoded string should be returned so that
        # the data can be compared to the expected value stored in the test profile.
        if b64decode is True and isinstance(data, str):
            data = BinaryVariable(base64.b64decode(data))
            if decode is True:
                # allow developer to decided if they want bytes or str
                data = self._decode_binary(data)
        elif isinstance(data, bytes):
            # data should never be returned as bytes, but just in case an old App is using an
            # older version of TcEx or if the TC Platform is writes binary data to the key value
            # store, decode the bytes to a string
            data = self._decode_binary(data)

        return data

    def binary_array(
        self,
        key: str,
        b64decode: bool = True,
        decode: bool = False,
    ) -> list[BinaryVariable | str] | None:
        """Read the value from key value store.

        The binary array write method iterates over the BinaryArray and base64 encodes the data,
        then decodes the bytes to string, and finally serializes the array before writing to the
        key value store.

        This method will deserialize the string, then iterate over the array and OPTIONALLY base64
        decode the data, and finally return the BinaryArray.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'BinaryArray')

        # get the data from the key value store
        data = self._get_data(key)
        if data is None:
            return None

        # reverse the order of the binary create/write method
        # 1. deserialize the data
        # 2. iterate over the array
        # 3. base64 decode the data

        # data should be a serialized string, but in case there are any legacy Apps that are
        # using an older version of TcEx, check for bytes and decode to string
        if isinstance(data, bytes):
            data = data.decode('utf-8')

        # deserialize the data
        _data: list[str] = self._deserialize_data(data)

        values = []
        for d in _data:
            if b64decode is True and isinstance(d, str):
                d = BinaryVariable(base64.b64decode(d))
                if decode is True:
                    # allow developer to decided if they want bytes or str
                    d = self._decode_binary(d)
            values.append(d)
        return values

    def key_value(
        self,
        key: str,
        resolve_embedded: bool = True,
    ) -> dict | None:
        """Read the value from key value store.

        KeyValue data should be stored as a JSON string.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'KeyValue')

        # get the data from the key value store
        data = self._get_data(key)
        if data is None:
            return None

        # deserialize the data
        data = self._deserialize_data(data)

        return self._process_key_value(data, resolve_embedded=resolve_embedded)

    def key_value_array(
        self,
        key: str,
        resolve_embedded: bool = True,
    ) -> list[dict] | None:
        """Read the value from key value store.

        KeyValueArray data should be stored as serialized string.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'KeyValueArray')

        data = self._get_data(key)
        if data is None:
            return None

        # data should be a serialized string, but in case there are any legacy Apps that are
        # using an older version of TcEx, check for bytes and decode to string
        if isinstance(data, bytes):
            data = data.decode()

        # Array type is serialized before writing to redis, deserialize the data
        _data: list[dict] = self._deserialize_data(data)

        values = []
        for d in _data:
            # d should be a base64 encoded string
            values.append(self._process_key_value(d, resolve_embedded=resolve_embedded))
        return values

    def raw(self, key: str) -> Any | None:
        """Read method of CRUD operation for raw data.

        Bytes input will be returned a as string as there is no way
        to determine data from redis originated as bytes or string.
        """
        if self._null_key_check(key) is True:
            return None

        return self.key_value_store.read(self.context, key.strip())

    def string(
        self,
        key: str,
        resolve_embedded: bool = True,
    ) -> StringVariable | None:
        """Read the value from key value store.

        The string write method serializes the string before writing to the key value store.

        This method will deserialize the string and finally return the StringArray data.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'String')

        # get the data from the key value store
        data = self._get_data(key)
        if data is None:
            return None

        # data should be a serialized string, but in case there are any legacy Apps that are
        # using an older version of TcEx, check for bytes and decode to string
        if isinstance(data, bytes):
            data = data.decode()

        # deserialize the data
        data = self._deserialize_data(data)

        # only resolve embedded variables if resolve_embedded is True and
        # the entire string does not exactly match a variable pattern
        if resolve_embedded and not self.utils.is_playbook_variable(data):
            data = self._read_embedded(data)

        # coerce data back to string, since technically TC doesn't support bool, int, etc
        return StringVariable(self._coerce_string_value(data))

    def string_array(self, key: str) -> list[StringVariable] | None:
        """Read the value from key value store.

        The string_array write method serializes the list of strings before writing to the key value
        store.

        This method will deserialize the list of strings and finally return the StringArray data.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'StringArray')

        # get the data from the key value store
        data = self._get_data(key)
        if data is None:
            return None

        # data should be a serialized string, but in case there are any legacy Apps that are
        # using an older version of TcEx, check for bytes and decode to string
        if isinstance(data, bytes):
            data = data.decode()

        # deserialize the data
        _data: list[str] = self._deserialize_data(data)

        # return array of StringVariables
        return [StringVariable(self._coerce_string_value(d)) for d in _data]

    def tc_batch(self, key: str) -> dict | None:
        """Read the value from key value store.

        The tc_batch write method serializes the string before writing to the key value store.

        This method will deserialize the string and finally return the TCBatch data.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'TCBatch')

        data = self._get_data(key)
        if data is None:
            return None

        # data should be a serialized string, but in case there are any legacy Apps that are
        # using an older version of TcEx, check for bytes and decode to string
        if isinstance(data, bytes):
            data = data.decode()

        return self._deserialize_data(data)

    def tc_entity(self, key: str) -> dict[str, str] | None:
        """Read the value from key value store.

        The tc_entity write method serializes the dict before writing to the key value store.

        This method will deserialize the string and finally return the TCEntity data.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'TCEntity')

        # get the data from the key value store
        data = self._get_data(key)
        if data is None:
            return None

        # data should be a serialized string, but in case there are any legacy Apps that are
        # using an older version of TcEx, check for bytes and decode to string
        if isinstance(data, bytes):
            data = data.decode()

        # deserialize the data
        return self._deserialize_data(data)

    def tc_entity_array(
        self,
        key: str,
    ) -> list[dict[str, str]] | None:
        """Read the value from key value store.

        The tc_entity_array write method serializes the list of dicts before writing to the key
        value store.

        This method will deserialize the list of dicts and finally return the TCEntityArray data.
        """
        if self._null_key_check(key) is True:
            return None

        # quick check to ensure an invalid key was not provided
        self._check_variable_type(key, 'TCEntityArray')

        # get the data from the key value store
        data = self._get_data(key)
        if data is None:
            return None

        # data should be a serialized string, but in case there are any legacy Apps that are
        # using an older version of TcEx, check for bytes and decode to string
        if isinstance(data, bytes):
            data = data.decode()

        # deserialize the data
        return self._deserialize_data(data)

    def variable(self, key: str | None, array: bool = False) -> bytes | dict | list | str | None:
        """Read method of CRUD operation for working with KeyValue DB.

        This method will automatically check to see if a single variable is passed
        or if "mixed" data is passed and return the results from the DB. It will also
        automatically determine the variable type to read.
        """
        value = key
        if value is not None and isinstance(key, str):
            key = key.strip()

            if re.match(self.utils.variable_playbook_match, key):
                value = self.any(key=key)
            else:
                # replace space patterns
                value = self._process_space_patterns(value)

                # key must be an embedded variable
                value = self._read_embedded(value)

        if array is True:
            if isinstance(value, (list, str)):
                value = self._to_array(value)
            elif value is None:
                value = []

        return value
