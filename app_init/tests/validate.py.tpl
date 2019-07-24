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

    % if output_data:
        for k, v in output_variables.items():<%use_if = True%>
        % for data in output_data:
            % if use_if:
            if k == '${data['variable']}':<%use_if = False%>
            % else:
            elif k == '${data['variable']}':
            % endif
                self.${data['method']}(v)
        % endfor
            else:
                assert False, 'Unknown output variable found in profile: {}'.format(k)
    % endif
    % for data in output_data:

    def ${data['method']}(self, data):
        """Assert for ${data['variable']}."""
        output_var = '${data['variable']}'
        passed, assert_error = self.validator.redis.data(
            output_var, data.pop('expected_output'), data.pop('op', '='), **data
        )
        assert passed, assert_error
    % endfor
