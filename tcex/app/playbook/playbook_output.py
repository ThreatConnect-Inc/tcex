"""Playbook ABC"""
# standard library
import logging
from typing import TYPE_CHECKING

# first-party
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module

if TYPE_CHECKING:
    # first-party
    from tcex.app.playbook.playbook import Playbook

# get tcex logger
logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


class PlaybookOutput(dict):
    """Playbook Output

    Args:
        playbook: An instance of Playbook.
    """

    def __init__(self, playbook: 'Playbook'):
        """Initialize the class properties."""
        super().__init__()
        self.playbook = playbook

    def process(self):
        """Create all stored output data to storage."""
        for key, value in self.items():
            self.playbook.create.variable(key, value)
