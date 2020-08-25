"""Job Args"""


class Args:
    """Job Args"""

    def __init__(self, parser: object):
        """Initialize class properties."""
        parser.add_argument('--tc_owner', required=True)
