"""TcEx JSON App Config"""
# standard library
import json
import logging
import os
from collections import OrderedDict
from pathlib import Path
from typing import Optional

# first-party
from tcex.app_config.models import JobJsonModel
from tcex.backports import cached_property
from tcex.pleb.singleton import Singleton

# get tcex logger
tcex_logger = logging.getLogger('tcex')


class JobJson(metaclass=Singleton):
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
    def model(self) -> 'JobJsonModel':
        """Return the Install JSON model."""
        return JobJsonModel(**self.contents)

    # TODO: [low] possibly add auto fix of version and program name and then uncomment this code.
    # def write(self):
    #     """Write current data file."""
    #     data = self.model.json(
    #         by_alias=True, exclude_defaults=True, exclude_none=True, indent=2, sort_keys=True
    #     )
    #     with self.fqfn.open(mode='w') as fh:
    #         fh.write(f'{data}\n')
