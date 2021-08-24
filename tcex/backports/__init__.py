"""Python Backports"""

# flake8: noqa
try:
    # standard library
    from functools import cached_property
except ImportError:
    # third-party
    from backports.cached_property import cached_property
