# -*- coding: utf-8 -*-
"""Validation file for testing profiles."""


class Validation:
    """Validation base class for App output validation."""

    def __init__(self, validator):
        """Initialize class properties."""
        self.validator = validator

    def validation(self, output_variables):
        """Validate Redis output data."""
        if output_variables is None:
            return
        % for data in output_data:

        if '${data.variable}' in output_variables:
            output_variable_data = output_variables.get('${data.variable}')
            self.${data.method}('${data.variable}', output_variable_data)
        % endfor
    % for data in output_data:

    def ${data.method}(self, variable, data):
        assert self.validator.redis.data(
            variable,
            data.get('expected_output', None),
            data.get('op', '='),
        )
    % endfor
