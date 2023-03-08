"""TcEx Generate Configurations CLI Command"""

# first-party
from tcex.app.config import AppSpecYml, TcexJson
from tcex.app.config.models import TcexJsonModel
from tcex.bin.bin_abc import BinABC


class SpecToolTcexJson(BinABC):
    """Generate App Config File"""

    def __init__(self, asy: AppSpecYml):
        """Initialize class properties."""
        super().__init__()
        self.asy = asy

        # properties
        self.filename = 'tcex.json'
        self.tj = TcexJson()

    def generate(self):
        """Generate the layout.json file data."""

        tcex_json_data = self.tj.model.dict()

        # update package name
        tcex_json_data['package']['app_name'] = self.asy.model.package_name
        return TcexJsonModel(**tcex_json_data)

    @staticmethod
    def generate_schema():
        """Return the schema for the install.json file."""
        return TcexJsonModel.schema_json(indent=2, sort_keys=True)
