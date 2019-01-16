# -*- coding: utf-8 -*-
"""Job Args"""


class Args(object):
    """Job Args"""

    def __init__(self, parser):
        """Initialize class properties."""
        parser.add_argument('--tc_owner', required=True)
