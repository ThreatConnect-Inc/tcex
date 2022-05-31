"""TcEx Generate Configurations CLI Command"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.app_config import TcexJson
from tcex.app_config.models.job_json_model import JobJsonModel
from tcex.bin.bin_abc import BinABC

if TYPE_CHECKING:
    # first-party
    from tcex.app_config import AppSpecYml


class SpecToolJobJson(BinABC):
    """Generate App Config File"""

    def __init__(self, asy: 'AppSpecYml'):
        """Initialize class properties."""
        super().__init__()
        self.asy = asy

        # properties
        self.tj = TcexJson(logger=self.log)

    def generate(self):
        """Generate the layout.json file data."""
        if self.asy.model.organization and self.asy.model.organization.feeds:
            for feed in self.asy.model.organization.feeds:
                _job_data = feed.job.dict(by_alias=True)
                app_name = self.tj.model.package.app_name.replace('_', ' ')

                # handle statically defined version in tcex.json file
                version = f'v{self.asy.model.program_version.major}'
                if self.tj.model.package.app_version:
                    version = self.tj.model.package.app_version

                _job_data['programName'] = f'{app_name} {version}'
                _job_data['programVersion'] = str(self.asy.model.program_version)
                yield feed.job_file, JobJsonModel(**_job_data)

    @staticmethod
    def generate_schema():
        """Return the schema for the install.json file."""
        return JobJsonModel.schema_json(indent=2, sort_keys=True)
