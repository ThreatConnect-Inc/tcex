# -*- coding: utf-8 -*-
"""External App Template."""
import json
import os

# Typically no changes are required to this file.


class ExternalApp(object):
    """Get the owners and indicators in the given owner."""

    def __init__(self, _tcex):
        """Initialize class properties."""
        self.tcex = _tcex
        self.args = None
        self.exit_message = 'Success'
        self.config = 'app_config.json'

    def done(self):
        """Perform cleanup operations and gracefully exit the App."""
        self.tcex.log.debug('Running done.')

    def inject_args_from_config(self):
        """Inject args from config as args."""
        if os.path.isfile(self.config):
            with open(self.config, 'r') as fh:
                config_data = json.load(fh)
            self.tcex.tcex_args.inject_params(config_data)
        else:
            self.tcex.log.error('Config file "{}" could not be found.'.format(self.config))
        self.args = self.tcex.args

    def run(self):
        """Run the App main logic."""
        self.tcex.log.info('No run logic provided.')

    def start(self):
        """Perform prep/startup operations."""
        self.tcex.log.debug('Running start.')
