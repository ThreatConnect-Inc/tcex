# -*- coding: utf-8 -*-
"""Job Args"""


class Args(object):
    """Job Args"""

    def __init__(self, _tcex):
        """Initialize class properties."""
        _tcex.parser.add_argument('--tc_owner', required=True)
        _tcex.parser.add_argument('--count_groups', action='store_true', default=False)
