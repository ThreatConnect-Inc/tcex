"""Service Args"""


class Args:
    """Playbook Args"""

    def __init__(self, parser: object):
        """Initialize class properties."""
        parser.add_argument('--example_input')
