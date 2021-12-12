"""Playbook ABC"""
# standard library
import base64
import json
import logging
from abc import ABC
from collections.abc import Iterable
from typing import Optional, Union

# first-party
from tcex.playbook.playbook_abc import PlaybookABC

# get tcex logger
logger = logging.getLogger('tcex')


class PlaybookWriteABC(PlaybookABC, ABC):
    """Playbook Write ABC"""

    def _create(
        self, key: str, value: Union[bytes, str], validate: Optional[bool] = True
    ) -> Optional[int]:
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

        try:
            return self.key_value_store.create(self._context, key.strip(), value)
        except RuntimeError as e:
            self.log.error(e)
        return None

    def _create_array(self, key: str, value: list, validate: Optional[bool] = True):
        """Create the value in Redis if applicable."""
        if key is None or value is None:
            self.log.warning('The key or value field is None.')
            return None

        # get variable type from variable value
        variable_type = self.variable_type(key)

        # Enhanced entity array is the wild-wild west, don't validate it
        if variable_type != 'TCEnhancedEntityArray':
            if validate and (not isinstance(value, Iterable) or isinstance(value, (str, dict))):
                raise RuntimeError(f'Invalid data provided for {variable_type}.')

            value = [
                *value
            ]  # spread the value so that we know it's a list (as opposed to an iterable)

        if variable_type == 'BinaryArray':
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
            if validate and not self._is_key_value_array(value):
                raise RuntimeError('Invalid data provided for KeyValueArray.')
        elif variable_type == 'StringArray':
            value_coerced = []
            for v in value:
                # coerce string values
                v = self._coerce_string_value(v)

                if validate and not isinstance(v, (type(None), str)):
                    raise RuntimeError('Invalid data provided for StringArray.')
                value_coerced.append(v)
            value = value_coerced
        elif variable_type == 'TCEntityArray':
            if validate and not self._is_tc_entity_array(value):
                raise RuntimeError('Invalid data provided for TcEntityArray.')

        # self.log.trace(f'pb create - context: {self._context}, key: {key}, value: {value}')
        try:
            value = json.dumps(value)
        except ValueError as e:  # pragma: no cover
            raise RuntimeError(f'Failed to serialize value ({e}).')

        try:
            return self.key_value_store.create(self._context, key.strip(), value)
        except RuntimeError as e:
            self.log.error(e)
        return None

    def create_raw(self, key: str, value: Union[bytes, int, str]) -> str:
        """Create method of CRUD operation for raw data.

        Raw data can only be a byte, str or int. Other data
        structures (dict, list, etc) must be serialized.

        Args:
            key: The variable to write to the DB.
            value: The data to write to the DB.
        """
        data = None
        if key is not None and value is not None:
            try:
                data = self.key_value_store.create(self._context, key.strip(), value)
            except RuntimeError as e:
                self.log.error(e)
        else:
            self.log.warning('The key or value field was None.')
        return data
