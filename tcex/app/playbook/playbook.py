"""TcEx Framework Playbook module"""
# standard library
import logging

# first-party
from tcex.app.key_value_store.key_value_store import KeyValueStore
from tcex.app.playbook.playbook_create import PlaybookCreate
from tcex.app.playbook.playbook_delete import PlaybookDelete
from tcex.app.playbook.playbook_output import PlaybookOutput
from tcex.app.playbook.playbook_read import PlaybookRead
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module
from tcex.pleb.cached_property import cached_property
from tcex.util.model import PlaybookVariableModel
from tcex.util.util import Util

# get tcex logger
logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


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
        key_value_store: KeyValueStore,
        context: str | None = None,
        output_variables: list | None = None,
    ):
        """Initialize the class properties."""
        self.context = context
        self.key_value_store = key_value_store
        self.output_variables = output_variables or []

        # properties
        self.log = logger
        self.util = Util()

    def check_key_requested(self, key: str) -> bool:
        """Return True if output key was requested by downstream app.

        Provide key should be in format "app.output".
        """
        variables = []
        for variable in self.output_variables:
            var = self.util.get_playbook_variable_model(variable)
            if isinstance(var, PlaybookVariableModel):
                variables.append(var.key)

        return key in variables

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
        return self.util.get_playbook_variable_type(variable)

    @cached_property
    def create(self) -> PlaybookCreate:
        """Return instance of PlaybookCreate"""
        if self.context is None:
            raise RuntimeError('Playbook context is required for PlaybookCreate.')

        return PlaybookCreate(self.context, self.key_value_store, self.output_variables)

    @cached_property
    def delete(self) -> PlaybookDelete:
        """Return instance of PlaybookDelete"""
        if self.context is None:
            raise RuntimeError('Playbook context is required for PlaybookDelete.')

        return PlaybookDelete(self.context, self.key_value_store)

    def is_variable(self, key: str) -> bool:
        """Return True if provided key is a properly formatted playbook variable."""
        return self.util.is_playbook_variable(key)

    @cached_property
    def output(self) -> PlaybookOutput:
        """Return instance of PlaybookOutput"""
        return PlaybookOutput(self)

    @cached_property
    def read(self) -> PlaybookRead:
        """Return instance of PlaybookRead"""
        if self.context is None:
            raise RuntimeError('Playbook context is required for PlaybookRead.')

        return PlaybookRead(self.context, self.key_value_store)
