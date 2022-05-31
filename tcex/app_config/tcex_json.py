"""TcEx JSON App Config"""
# standard library
import json
import logging
import os
from collections import OrderedDict
from pathlib import Path
from typing import Optional

# third-party
import colorama as c

# first-party
from tcex.app_config.install_json import InstallJson
from tcex.app_config.models import TcexJsonModel
from tcex.app_config.tcex_json_update import TcexJsonUpdate
from tcex.backports import cached_property

# get tcex logger
tcex_logger = logging.getLogger('tcex')


class TcexJson:
    """Provide a model for the tcex.json config file."""

    def __init__(
        self,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize class properties."""
        filename = filename or 'tcex.json'
        path = path or os.getcwd()
        self.log = logger or tcex_logger

        # properties
        self.fqfn = Path(os.path.join(path, filename))
        self.ij = InstallJson(logger=self.log)

    @cached_property
    def contents(self) -> dict:
        """Return tcex.json file contents."""
        _contents = {}

        if self.fqfn.is_file():
            try:
                with self.fqfn.open() as fh:
                    _contents = json.load(fh, object_pairs_hook=OrderedDict)
            except OSError:  # pragma: no cover
                self.log.error(
                    f'feature=tcex-json, exception=failed-reading-file, filename={self.fqfn}'
                )
        else:  # pragma: no cover
            self.log.error(f'feature=tcex-json, exception=file-not-found, filename={self.fqfn}')

        return _contents

    @cached_property
    def model(self) -> 'TcexJsonModel':
        """Return the Install JSON model."""
        return TcexJsonModel(**self.contents)

    def print_warnings(self):
        """Print warning messages for tcex.json file."""

        # raise error if tcex.json is missing app_name field
        if self.model.package.app_name is None:  # pragma: no cover
            raise RuntimeError('The tcex.json file is missing the package.app_name field.')

        # log warning for old Apps
        if self.model.package.app_version is not None:
            print(
                f'{c.Fore.YELLOW}'
                'WARNING: The tcex.json file defines "app_version" which should only be '
                'defined in legacy Apps. Removing the value can cause the App to be treated '
                'as a new App by TcExchange. Please remove "app_version" when appropriate.'
                f'{c.Fore.RESET}'
            )

    @property
    def update(self) -> 'TcexJsonUpdate':
        """Return InstallJsonUpdate instance."""
        return TcexJsonUpdate(tj=self)

    def write(self):
        """Write current data file."""
        data = self.model.json(exclude_defaults=True, exclude_none=True, indent=2, sort_keys=True)
        with self.fqfn.open(mode='w') as fh:
            fh.write(f'{data}\n')
