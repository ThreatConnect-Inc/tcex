"""Service Args"""
from argparse import ArgumentParser


class Args:
    """Playbook Args"""

    def __init__(self, parser: ArgumentParser):
        """Initialize class properties."""
        parser.add_argument('--example_input')
