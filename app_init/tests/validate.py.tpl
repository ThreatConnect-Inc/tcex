# -*- coding: utf-8 -*-
"""Validate App outputs Class."""


class Validate:
    """Validate base class for App output validation."""

    def __init__(self, validator):
        """Initialize class properties."""
        self.validator = validator

    def validate(self, output_variables):
        """Validate Redis output data."""
        if output_variables is None:
            return
        % for data in output_data:

        if '${data['variable']}' in output_variables:
            data = output_variables.get('${data['variable']}')
            self.${data['method']}(data)
        % endfor
    % for data in output_data:

    def ${data['method']}(self, data):
        """Assert output data for variable ${data['variable']}."""
        validation_data = self.validator.redis.data(
            '${data['variable']}',
            data.get('expected_output'),
            data.get('op', '='),
        )
        validation_error = (
            '\nApp Data: {}\nExpected Data: {}\nDetails: {}\n'.format(
                validation_data.get('app_data'),
                validation_data.get('test_data'),
                validation_data.get('details')
            )
        )
        assert validation_data.get('status', False), validation_error
    % endfor
