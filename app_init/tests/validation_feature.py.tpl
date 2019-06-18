# -*- coding: utf-8 -*-
"""Validation file for testing profiles."""
from ..validation import Validation


class ValidationFeature(Validation):
    """Validation for Feature ${feature}, File ${file}.

    This file will only be auto-generated once to ensure any changes are not overwritten.
    """

    def __init__(self, validator):
        """Initialize class properties."""
        super(ValidationFeature, self).__init__(validator)
