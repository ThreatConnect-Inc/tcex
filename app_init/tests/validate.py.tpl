# -*- coding: utf-8 -*-
"""Validate App outputs Class."""
# flake8: noqa
# pylint: disable=line-too-long
import inspect


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
            # get method name from variable name
            method_name = self.validator.utils.variable_method_name(k)
            if hasattr(self, method_name):
                method = getattr(self, method_name)  # get the validation method by name
                if 'variable' in [p.name for p in inspect.signature(method).parameters.values()]:
                    method(k, dict(v))  # methods with new signature
                else:
                    method(dict(v))  # methods with old signature
            else:
                self.dynamic_output_variable(k, dict(v))

    def dynamic_output_variable(self, variable, data):
        """Assert for dynamic output variables."""
        passed, assert_error = self.validator.redis.data(
            variable, data.pop('expected_output'), data.pop('op', '='), **data
        )
        assert passed, assert_error

    % for data in output_data:
    def ${data['method']}(self, variable, data):
        """Assert for ${data['variable']}."""
        expected_output = data.pop('expected_output')
        op = data.pop('op', '=')

        # assert variable data
        passed, assert_error = self.validator.redis.data(variable, expected_output, op, **data)
        assert passed, assert_error

    % endfor
