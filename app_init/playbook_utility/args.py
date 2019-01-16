# -*- coding: utf-8 -*-
"""Playbook Args"""


class Args(object):
    """Playbook Args"""

    def __init__(self, parser):
        """Initialize class properties."""
        parser.add_argument('--indent', default=4)
        parser.add_argument('--json_data', required=True)
        parser.add_argument('--sort_keys', action='store_true')
