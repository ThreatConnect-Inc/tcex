"""TcEx JSON App Config"""
# standard library
import json
import logging
import os
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path

from .models import JobJsonModel


class JobJson:
    """Provide a model for the tcex.json config file."""

    def __init__(self, filename=None, path=None, logger=None):
        """Initialize class properties."""
        filename = filename or 'tcex.json'
        path = path or os.getcwd()
        self.log = logger or logging.getLogger('tcex_json')

        # properties
        self.fqfn = Path(os.path.join(path, filename))

    @property
    @lru_cache
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

    @property
    # @lru_cache
    def data(self) -> JobJsonModel:
        """Return the Install JSON model."""
        return JobJsonModel(**self.contents)

    def write(self) -> None:
        """Write current data file."""
        data = self.data.json(
            by_alias=True, exclude_defaults=True, exclude_none=True, indent=2, sort_keys=True
        )
        with self.fqfn.open(mode='w') as fh:
            fh.write(f'{data}\n')
