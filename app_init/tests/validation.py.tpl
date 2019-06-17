# -*- coding: utf-8 -*-
"""Validation file for testing profiles."""

class Validation:
    """Validation for Feature ${feature}, File ${file}.

    This file will only be auto-generated once to ensure any changes are not overwritten.
    """

    def __init__(self, validator):
        """Initialize class properties."""
        self.validator = validator

    def validation(self, output_variables):
        """Validate Redis output data."""
        if output_variables is None:
            return
        % for variable in output_variables:

        if '${variable}' in output_variables:
            output_variable_data = output_variables.get('${variable}')
            assert self.validator.redis.data(
                '${variable}',
                output_variable_data.get('expected_output', None),
                output_variable_data.get('op', '='),
            )
        % endfor
