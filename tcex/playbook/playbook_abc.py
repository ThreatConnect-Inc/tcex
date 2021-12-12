"""Playbook ABC"""
# standard library
import logging
import re
from abc import ABC
from typing import List, Optional, Union

# first-party
from tcex.key_value_store import KeyValueApi, KeyValueRedis
from tcex.utils.utils import Utils

# get tcex logger
logger = logging.getLogger('tcex')


class PlaybookABC(ABC):
    """Playbook ABC

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
        context: str,
        output_variables: list,
    ):
        """Initialize the class properties."""
        self._context = context
        self._output_variables = output_variables
        self.key_value_store = key_value_store

        # properties
        self._output_variables_by_key = None
        self._output_variables_by_type = None
        self.log = logger
        self.utils = Utils()

    def _coerce_string_value(self, value: Union[bool, float, int, str]) -> str:
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

    @staticmethod
    def _decode_binary(data: bytes) -> str:
        """Return decoded bytes data handling data written by java apps."""
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:  # pragma: no cover
            # for data written an upstream java App
            data = data.decode('latin-1')
        return data

    @staticmethod
    def _is_key_value(data: dict) -> bool:
        """Return True if provided data has proper structure for Key Value."""
        if data is None:
            return False
        return all(x in data for x in ['key', 'value'])

    def _is_key_value_array(self, data: List[dict]) -> bool:
        """Return True if provided data has proper structure for Key Value Array."""
        for d in data:
            if not self._is_key_value(d):
                return False
        return True

    @staticmethod
    def _is_tc_entity(data: dict) -> bool:
        """Return True if provided data has proper structure for TC Entity."""
        if data is None:
            return False
        return all(x in data for x in ['id', 'value', 'type'])

    def _is_tc_entity_array(self, data: List[dict]) -> bool:
        """Return True if provided data has proper structure for TC Entity Array."""
        for d in data:
            if not self._is_tc_entity(d):
                return False
        return True

    def _parse_output_variables(self) -> None:
        """Parse the output variables provided to Playbook Class.

        Example Variable Format:

        ['#App:1234:status!String', '#App:1234:status_code!String']
        """
        self._output_variables_by_key = {}
        self._output_variables_by_type = {}
        for ov in self._output_variables:
            # parse the variable to get individual parts
            parsed_variable = self.parse_variable(ov)
            variable_key = parsed_variable.get('key')
            variable_type = parsed_variable.get('type')

            # store the variables in dict by key (e.g. "status_code")
            self._output_variables_by_key[variable_key] = {'variable': ov}

            # store the variables in dict by key-type (e.g. "status_code-String")
            self._output_variables_by_type[f'{variable_key}-{variable_type}'] = {'variable': ov}

    @staticmethod
    def _process_space_patterns(string: str) -> str:
        r"""Return the string with \s replace with spaces."""
        # replace "\s" with a space only for user input.
        # using '\\s' will prevent replacement.
        string = re.sub(r'(?<!\\)\\s', ' ', string)
        string = re.sub(r'\\\\s', r'\\s', string)
        return string

    @staticmethod
    def _to_array(value: Optional[Union[List, str]]) -> List:
        """Return the provided array as a list."""
        if value is None:
            # Adding none value to list breaks App logic. It's better to not request
            # Array and build array externally if None values are required.
            value = []
        elif not isinstance(value, list):
            value = [value]
        return value

    @property
    def _variable_array_types(self) -> List[str]:
        """Return list of standard playbook array variable types."""
        return [
            'BinaryArray',
            'KeyValueArray',
            'StringArray',
            'TCEntityArray',
            'TCEnhancedEntityArray',
        ]

    @property
    def _variable_single_types(self) -> List[str]:
        """Return list of standard playbook single variable types."""
        return [
            'Binary',
            'KeyValue',
            'String',
            'TCEntity',
            'TCEnhancedEntity',
        ]

    @property
    def _variable_types(self) -> List[str]:
        """Return list of standard playbook variable types."""
        return self._variable_single_types + self._variable_array_types

    def parse_variable(self, variable: str) -> dict:  # pragma: no cover
        """Set placeholder for child method."""
        raise NotImplementedError('Implemented in child class')

    def variable_type(self, variable: str) -> str:  # pragma: no cover
        """Set placeholder for child method."""
        raise NotImplementedError('Implemented in child class')
