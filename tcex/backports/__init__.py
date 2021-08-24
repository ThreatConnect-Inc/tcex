"""Python Backports"""

# flake8: noqa
try:
    # standard library
    from functools import cached_property
except ImportError:
    # third-party
    from .backport_cached_property import cached_property
