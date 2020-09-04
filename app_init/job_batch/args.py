"""Job Args"""
from argparse import ArgumentParser


class Args:
    """Job Args"""

    def __init__(self, parser: ArgumentParser):
        """Initialize class properties."""
        parser.add_argument('--tc_owner', required=True)
