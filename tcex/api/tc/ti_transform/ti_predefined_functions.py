"""TcEx Framework Module"""

# first-party
from tcex.util import Util

to_upper_case = str.upper
to_lower_case = str.lower
to_title_case = str.title

prepend = '{prefix} {}'.format
append = '{} {suffix}'.format


def replace(value: str, find: str, replace_with: str) -> str:
    """Replace value in string."""
    return value.replace(find, replace_with)


def format_datetime(value: str):
    """Format datetime."""
    return Util.any_to_datetime(value).strftime('%Y-%m-%dT%H:%M:%SZ')
