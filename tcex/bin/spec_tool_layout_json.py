"""TcEx Generate Configurations CLI Command"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.app_config.models import LayoutJsonModel
from tcex.bin.bin_abc import BinABC

if TYPE_CHECKING:
    # first-party
    from tcex.app_config import AppSpecYml


class SpecToolLayoutJson(BinABC):
    """Generate App Config File"""

    def __init__(self, asy: 'AppSpecYml'):
        """Initialize class properties."""
        super().__init__()
        self.asy = asy

        # properties
        self.filename = 'layout.json'

    def generate(self):
        """Generate the layout.json file data."""

        layout_json_data = {
            'inputs': self.asy.model.inputs,
            'outputs': self.asy.model.outputs,
        }
        return LayoutJsonModel(**layout_json_data)

    @staticmethod
    def generate_schema():
        """Return the schema for the install.json file."""
        return LayoutJsonModel.schema_json(indent=2, sort_keys=True)
