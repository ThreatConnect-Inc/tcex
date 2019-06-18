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

    % for method in output_methods:

    def ${method}(self, variable, data):
        assert self.validator.redis.data(
            '${variable}',
            data.get('expected_output', None),
            data.get('op', '='),
        )
    % endfor
