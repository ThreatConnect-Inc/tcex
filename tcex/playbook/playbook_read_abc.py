"""Playbook ABC"""
# standard library
import base64
import json
import logging
import re
from abc import ABC
from collections import OrderedDict
from typing import Any, Optional, Union

# first-party
from tcex.playbook.playbook_abc import PlaybookABC
from tcex.pleb.registry import registry

# get tcex logger
logger = logging.getLogger('tcex')


class PlaybookReadABC(PlaybookABC, ABC):
    """Playbook Read ABC"""

    def _get_data(self, key: str) -> any:
        """Get the value from Redis if applicable."""
        value = None
        try:
            value = self.key_value_store.read(self._context, key.strip())
        except RuntimeError as e:
            self.log.error(e)
        return value

    @staticmethod
    def _load_data(value: str) -> dict:
        """Return the loaded JSON value or raise an error."""
        try:
            return json.loads(value, object_pairs_hook=OrderedDict)
        except ValueError as e:  # pragma: no cover
            raise RuntimeError(f'Failed to JSON load data "{value}" ({e}).')

    def _null_key_check(self, key: Any) -> bool:
        """Return False if value is not null."""
        if key is None:
            self.log.warning('The provided key as None.')
            return True

        if self.utils.is_playbook_variable(key):
            # only log key if it's a variable
            self.log.debug(f'read variable {key}')
        return False

    def _process_binary(
        self, data: str, b64decode: bool, decode: bool, serialized: bool
    ) -> Optional[Union[str, bytes]]:
        """Process the provided."""
        if data is not None:
            # Single type are serialized, array types are not
            if serialized is True:
                data = self._load_data(data)

            if b64decode is True:
                data = base64.b64decode(data)
                if decode is True:
                    # allow developer to decided if they want bytes or str
                    data = self._decode_binary(data)
            elif isinstance(data, bytes):
                # data is likely returned base64 encoded bytes string, the App
                # should get the base64 as a str if b64decode is False
                data = data.decode()

        return data

    def _process_key_value(
        self, data: str, resolve_embedded: bool, serialized: bool
    ) -> Optional[dict]:
        """Read the value from key value store.

        KeyValue data should be stored as a JSON string.
        """
        if data is not None:
            # decode in case data comes back from kvstore as bytes
            if isinstance(data, bytes):
                data = data.decode()

            # Single type are serialized, array types are not
            if serialized is True:
                data = self._load_data(data)

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
                value = data.get('value')
                if self.utils.is_playbook_variable(value):
                    # any type can be nested, but no further nesting is supported
                    data['value'] = self.read_any(value)
                else:
                    # read embedded is less efficient and has more caveats
                    data['value'] = self._read_embedded(value)

        return data

    def _process_string(self, data: str, resolve_embedded: bool, serialized: bool) -> Optional[str]:
        """Process the provided."""
        if data is not None:
            # decode in case data comes back from kvstore as bytes
            if isinstance(data, bytes):
                data = data.decode()

            # Single type are serialized, array types are not
            if serialized is True:
                data = self._load_data(data)

            # only resolve embedded variables if resolve_embedded is True and
            # the entire string does not exactly match a variable pattern
            if resolve_embedded and not self.utils.is_playbook_variable(data):
                data = self._read_embedded(data)

            # coerce data back to string, since technically TC doesn't support bool, int, etc
            data = self._coerce_string_value(data)

        return data

    def _process_tc_entity(self, data: str, serialized: bool) -> Optional[dict]:
        """Process the provided."""
        if data is not None:
            # decode in case data comes back from kvstore as bytes
            if isinstance(data, bytes):
                data = data.decode()

            # Single type are serialized, array types are not
            if serialized is True:
                data = self._load_data(data)

        return data

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
            if match.group('origin') == '#':  # pb-variable
                v = self.read_any(variable)
            elif match.group('origin') == '&':  # tc-variable
                v = registry.resolve_variable(variable)

            # TODO: [high] should this behavior be changed in 3.0?
            self.log.trace(f'embedded variable: {variable}, value: {v}')
            if isinstance(v, (dict, list)):
                v = json.dumps(v)
                # for KeyValueArray with nested dict/list type replace the
                # quoted value to ensure the resulting data is loadable JSON
                value = value.replace(f'"{variable}"', v)

            if v is not None:
                # only replace variable if a non-null value is returned from kv store
                # APP-1030 need to revisit this to handle variable references in kv/kv_arrays that
                # are None.  Would like to be able to say if value is just the variable reference,
                # sub None value, else insert '' in string.  That would require a kv-specific
                # version of this method that gets the entire list/dict instead of just the string.
                value = value.replace(variable, v)
        return value

    def _wrap_embedded_keyvalue(self, data: str) -> str:
        """Wrap keyvalue embedded variable in double quotes."""
        # TODO: need to verify if core still sends improper JSON for KeyValueArrays
        if data is not None:  # pragma: no cover
            variables = []
            for v in re.finditer(self.utils.variable_playbook_keyvalue_embedded, data):
                variables.append(v.group(0))

            for var in set(variables):  # recursion over set to handle duplicates
                # pull (#App:1441:embedded_string!String) from (": #App:1441:embedded_string!String)
                variable_string = re.search(self.utils.variable_playbook_parse, var).group(0)
                # reformat to replace the correct instance only, handling the case where a variable
                # is embedded multiple times in the same key value array.
                data = data.replace(var, f'": "{variable_string}"')
        return data

    def read_any(self, key: str) -> Optional[Union[bytes, dict, list, str]]:
        """Set placeholder for child method."""
        raise NotImplementedError('Implemented in child class')

    def read_raw(self, key: str) -> Optional[any]:
        """Read method of CRUD operation for raw data.

        Bytes input will be returned a as string as there is no way
        to determine data from redis originated as bytes or string.
        """
        if self._null_key_check(key) is True:
            return None

        return self.key_value_store.read(self._context, key.strip())
