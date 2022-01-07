"""TcEx Utilities Variables Operations Module"""
# standard library
import re
from typing import Any, List

# first-party
from tcex.utils.models import PlaybookVariableModel


class BinaryVariable(bytes):
    """Bytes object with internal variable type field. Used when reading playbook variables"""

    _variable_type = 'Binary'


class StringVariable(str):
    """String object with internal variable type field. Used when reading playbook variables"""

    _variable_type = 'String'


class Variables:
    """TcEx Utilities Variables Class"""

    def get_playbook_variable_model(self, variable: str) -> 'PlaybookVariableModel':
        """Return data model of playbook variable (e.g., #App:1234:output!String)."""
        data = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self.variable_playbook_match, variable):
                var = re.search(self.variable_playbook_parse, variable)
                data = PlaybookVariableModel(**var.groupdict())
        return data

    def get_playbook_variable_type(self, variable: str) -> str:
        """Get variable type"""
        model = self.get_playbook_variable_model(variable)
        return 'String' if model is None else model.type

    def is_playbook_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted playbook variable."""
        if not isinstance(key, str):
            return False
        if re.match(self.variable_playbook_match, key):
            return True
        return False

    def is_tc_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted tc variable."""
        if not isinstance(key, str):
            return False
        if re.match(self.variable_tc_match, key):
            return True
        return False

    @property
    def variable_expansion_pattern(self):
        """Regex pattern to match and parse a playbook variable.

        Playbook Variable: #App:334:example.service_input!String
        TC Variable: &{TC:TEXT:4dc9202e-6945-4364-aa40-4b47655046d2}
        """
        return re.compile(
            # Origin:
            # PB-Variable: "#"
            # TC-Variable: "&"
            r'(?P<origin>#|&)'
            r'(?:\{)?'  # drop "{"
            # Provider:
            # PB-Variable: literal "App"
            # TC-Variable: provider (e.g. TC|Vault)
            r'(?P<provider>[A-Za-z]+):'
            # ID:
            # PB-Variable: Job ID (e.g., 334)
            # TC-Variable: One of (FILE|KEYCHAIN|TEXT)
            r'(?P<id>[\w]+):'
            # Lookup:
            # PB-Variable: variable id (e.g., API Token)
            # TC-Variable: variable id (e.g., 4dc9202e-6945-4364-aa40-4b47655046d2)
            r'(?P<lookup>[A-Za-z0-9_\.\-\[\]]+)'
            r'(?:\})?'  # drop "}"
            # Type
            # PB-Variable: variable type (e.g., String|StringArray)
            # TC-Variable: N/A
            r'(?:!(?P<type>[A-Za-z0-9_-]+))?'
        )

    @property
    def variable_playbook_match(self) -> Any:
        """Return compiled re pattern."""
        return re.compile(fr'^{self.variable_playbook_pattern}$')

    def variable_playbook_method_name(self, variable: str) -> str:
        """Convert variable name to a valid method name.

        #App:9876:string.operation!String -> string_operation_string

        Args:
            variable: The variable name to convert.
        """
        method_name = None
        if variable is not None:
            variable = variable.strip()
            if re.match(self.variable_playbook_match, variable):
                var = re.search(self.variable_playbook_parse, variable)
                variable_name = var.group(3).replace('.', '_').lower()
                variable_type = var.group(4).lower()
                method_name = f'{variable_name}_{variable_type}'
        return method_name

    @property
    def variable_playbook_pattern(self) -> str:
        """Regex pattern to match and parse a playbook variable."""
        return (
            # App Type: one of the following types (APP|Trigger)
            r'#(?P<app_type>[A-Za-z]+)'
            # TODO: [high] confirm this is correct
            # Job ID: the Id of the running job (e.g, 7979).
            r':(?P<job_id>[\d]+)'
            # Key: the variable key (e.g., api_token)
            r':(?P<key>[A-Za-z0-9_\.\-\[\]]+)'
            # Type: one of the following types
            #     (Binary|BinaryArray|KeyValue|KeyValueArray|
            #      String|StringArray|TCEntity|TCEntityArray|
            #      or <custom>)
            r'!(?P<type>StringArray|BinaryArray|KeyValueArray'
            r'|TCEntityArray|TCEnhancedEntityArray'
            r'|String|Binary|KeyValue|TCEntity|TCEnhancedEntity'
            r'|(?:(?!String)(?!Binary)(?!KeyValue)'
            r'(?!TCEntity)(?!TCEnhancedEntity)'
            r'[A-Za-z0-9_-]+))'  # variable type (custom)
        )

    @property
    def variable_playbook_parse(self) -> Any:
        """Return compiled re pattern."""
        return re.compile(self.variable_playbook_pattern)

    @property
    def variable_playbook_keyvalue_embedded(self) -> Any:
        """Return compiled re pattern."""
        return re.compile(fr'(?:\"\:\s?)[^\"]?{self.variable_playbook_pattern}')

    @property
    def variable_tc_match(self):
        """Return regex pattern for tc variable match."""
        return re.compile(fr'^{self.variable_tc_pattern}$')

    @property
    def variable_tc_pattern(self):
        """Return regex pattern for tc variable."""
        return (
            # Origin "&"
            r'(?:&)'
            r'(?:\{)'
            # Provider: who provides the variable (e.g. TC|Vault)
            r'(?P<provider>[A-Za-z]+):'
            # Type: one of (FILE|KEYCHAIN|TEXT)
            r'(?P<type>FILE|KEYCHAIN|TEXT):'
            # Key: variable id (e.g., 4dc9202e-6945-4364-aa40-4b47655046d2)
            r'(?P<key>[A-Za-z0-9_\.\-\[\]]+)'
            r'(?:\})'
        )

    @property
    def variable_tc_parse(self):
        """Return regex pattern for tc variable search."""
        return re.compile(self.variable_tc_pattern)

    @property
    def variable_playbook_array_types(self) -> List[str]:
        """Return list of standard playbook array variable types."""
        return [
            'BinaryArray',
            'KeyValueArray',
            'StringArray',
            'TCEntityArray',
            'TCEnhancedEntityArray',
        ]

    @property
    def variable_playbook_single_types(self) -> List[str]:
        """Return list of standard playbook single variable types."""
        return [
            'Binary',
            'KeyValue',
            'String',
            'TCEntity',
            'TCEnhancedEntity',
        ]

    @property
    def variable_playbook_types(self) -> List[str]:
        """Return list of standard playbook variable types."""
        return self.variable_playbook_single_types + self.variable_playbook_array_types
