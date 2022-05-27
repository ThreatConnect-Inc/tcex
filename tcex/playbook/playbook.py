"""TcEx Framework Playbook module"""
# standard library
import logging
from typing import Optional, Union

# first-party
from tcex.backports import cached_property
from tcex.key_value_store import KeyValueApi, KeyValueRedis
from tcex.playbook.playbook_create import PlaybookCreate
from tcex.playbook.playbook_delete import PlaybookDelete
from tcex.playbook.playbook_output import PlaybookOutput
from tcex.playbook.playbook_read import PlaybookRead
from tcex.utils.utils import Utils

# get tcex logger
logger = logging.getLogger('tcex')


class Playbook:
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
    ):
        """Initialize the class properties."""
        self.context = context
        self.key_value_store = key_value_store
        self.output_variables = output_variables or []

        # properties
        self.log = logger
        self.utils = Utils()

    def check_key_requested(self, key: str) -> bool:
        """Return True if output key was requested by downstream app.

        Provide key should be in format "app.output".
        """
        return key in [
            self.utils.get_playbook_variable_model(variable).key
            for variable in self.output_variables
        ]

    def check_variable_requested(self, variable: str) -> bool:
        """Return True if output variable was requested by downstream app.

        Provide variable should be in format of "#App:1234:app.output!String".
        """
        return variable in self.create.output_variables

    def get_variable_type(self, variable: str) -> str:
        """Get the Type from the variable string or default to String type.

        The default type is "String" for those cases when the input variable is
        contains not "DB variable" and is just a String.

        Example Variable:

        #App:1234:output!StringArray returns **StringArray**

        Example String:

        "My Data" returns **String**
        """
        return self.utils.get_playbook_variable_type(variable)

    @cached_property
    def create(self) -> 'PlaybookCreate':
        """Return instance of PlaybookCreate"""
        return PlaybookCreate(self.context, self.key_value_store, self.output_variables)

    @cached_property
    def delete(self) -> 'PlaybookDelete':
        """Return instance of PlaybookDelete"""
        return PlaybookDelete(self.context, self.key_value_store)

    def is_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted playbook variable."""
        return self.utils.is_playbook_variable(key)

    @cached_property
    def output(self) -> 'PlaybookOutput':
        """Return instance of PlaybookOutput"""
        return PlaybookOutput(self)

    @cached_property
    def read(self) -> 'PlaybookRead':
        """Return instance of PlaybookRead"""
        return PlaybookRead(self.context, self.key_value_store)
