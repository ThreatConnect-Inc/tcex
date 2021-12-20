"""Playbook ABC"""
# standard library
import logging
from typing import TYPE_CHECKING, Any, Optional

# first-party
from tcex.utils.utils import Utils

if TYPE_CHECKING:
    # first-party
    from tcex.playbook.playbook import Playbook

# get tcex logger
logger = logging.getLogger('tcex')


class PlaybookOutput:
    """Playbook Output

    Args:
        playbook: An instance of Playbook.
    """

    def __init__(self, playbook: 'Playbook') -> None:
        """Initialize the class properties."""
        self.playbook = playbook

        # properties
        self.data = {}
        self.utils = Utils()

    def add(
        self, key: str, value: Any, variable_type: str, append_array: Optional[bool] = True
    ) -> None:
        """Add dynamic output data to playbook.output module.

        This method provides an alternative and more dynamic way to create output variables in an
        App. Instead of storing the output data manually and writing all at once the data can be
        stored inline, when it is generated and then written before the App exits. Since the create
        method is always called before exit (success or failure), the data is always written to the
        kv store.

        Example:
        colors = ['blue', 'red', 'yellow']:
        tcex.playbook.output.add('app.colors', colors, 'StringArray')

        # this is called by the template and should not be called manually
        tcex.playbook.output.create()  #  writes the output stored in data

        Output Data Structure:
        {
            "app.colors-StringArray": {
                "key": "app.colors",
                "type": "StringArray",
                "value": ["blue", "red", "yellow"]
            }
        }

        Args:
            key: The variable name to write to storage.
            value: The value to write to storage.
            variable_type: The variable type being written.
            append_array: If True arrays will be appended instead of being overwritten.
        """

        # in older versions of TC Exchange it was possible to have the key be duplicated,
        # if the type was different. however, with the start of layout based Apps this
        # stopped being supported by the TC Platform. having to track the name by index
        # (key-variable_type) is still done for backwards compatibility.
        index = f'{key}-{variable_type}'

        # create the unique index so that variable can be updated
        self.data.setdefault(index, {})
        if value is None:
            if variable_type not in self.utils.variable_playbook_array_types:
                # never append or store None values if not an array
                return

            if not append_array and variable_type in self.utils.variable_playbook_array_types:
                # Only store none for array types when append is True
                return

        # set the key and value, if not previously defined
        self.data[index].setdefault('key', key)
        self.data[index].setdefault('type', variable_type)

        # handle all value types (e.g. single and array)
        if variable_type in self.utils.variable_playbook_array_types and append_array is True:
            if isinstance(value, list):
                self.data[index].setdefault('value', []).extend(value)
            else:
                self.data[index].setdefault('value', []).append(value)
        else:
            self.data[index]['value'] = value

    def create(self):
        """Create all stored output data to storage."""
        for data in self.data.values():
            self.playbook.create.variable(data.get('key'), data.get('value'), data.get('type'))
