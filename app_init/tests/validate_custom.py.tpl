# -*- coding: utf-8 -*-
"""Validate custom test case class."""
from .validate import Validate


class ValidateCustom(Validate):
    """Validate for Feature ${feature}

    This file will only be auto-generated once to ensure any changes are not overwritten.
    """

    def __init__(self, validator):  # pylint: disable=useless-super-delegation
        """Initialize class properties."""
        super(ValidateCustom, self).__init__(validator)
