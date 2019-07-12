# -*- coding: utf-8 -*-
"""Validate App outputs Class."""


class Validate(object):
    """Validate base class for App output validation."""

    def __init__(self, validator):
        """Initialize class properties."""
        self.validator = validator

    def validate(self, output_variables):
        """Validate Redis output data."""
        if output_variables is None:
            return

        for k, v in output_variables.items():
        % for data in output_data:
            if '${data['variable']}' == k:
                self.${data['method']}(v)
        % endfor
    % for data in output_data:

    def ${data['method']}(self, data):
        """Assert output data for variable ${data['variable']}."""
        passed, assert_error = self.validator.redis.data(
            '${data['variable']}',
            data.get('expected_output'),
            data.get('op', '='),
        )
        assert passed, assert_error
    % endfor
