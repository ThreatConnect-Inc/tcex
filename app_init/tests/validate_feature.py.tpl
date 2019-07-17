# -*- coding: utf-8 -*-
"""Validate feature test case class."""
from tcex.testing.monkeypatch import monkeypatch # pylint: disable=W0611
from ..validate import Validate


class ValidateFeature(Validate):
    """Validate for Feature ${feature}, File ${file}.

    This file will only be auto-generated once to ensure any changes are not overwritten.
    """

    def __init__(self, validator):  # pylint: disable=useless-super-delegation
        """Initialize class properties."""
        super(ValidateFeature, self).__init__(validator)
