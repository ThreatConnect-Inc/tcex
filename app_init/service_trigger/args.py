# -*- coding: utf-8 -*-
"""Playbook Args"""


class Args:
    """Playbook Args"""

    def __init__(self, parser):
        """Initialize class properties."""
        parser.add_argument('--example_input')
