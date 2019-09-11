# -*- coding: utf-8 -*-
"""Test the TcEx Metrics Module."""
import os
import sys
from tcex import TcEx
from tcex import Benchmark, Debug, FailOnInput, FailOnOutput, IterateOnArg, OnException, OnSuccess
from ..conftest import _config_data


# pylint: disable=W0201
class TestDecorators:
    """Test the TcEx Decorators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.tcex = None

    def setup_method(self):
        """Setup before each test case is called."""
        _config_data['arg1'] = 'arg1'
        _config_data['fail_on_enabled'] = True
        _config_data['fail_on_disabled'] = False
        _config_data['fail_on_string'] = 'false'
        # _config_data['iterate_on'] = ['one', 'two', 'three']
        _config_data['iterate_on'] = 'iterate_on'
        _config_data['none'] = None
        _config_data['null'] = 'null'
        _config_data['tc_log_file'] = self.tc_log_file
        sys.argv = sys.argv[:1]
        self.tcex = TcEx(config=_config_data)
        self.args = self.tcex.args

    @property
    def tc_log_file(self):
        """Return config file name for current test case."""
        test_data = os.getenv('PYTEST_CURRENT_TEST').split(' ')[0].split('::')
        test_feature = test_data[0].split('/')[1].replace('/', '-')
        test_name = test_data[-1].replace('/', '-').replace('[', '-')
        return os.path.join(test_feature, '{}.log'.format(test_name))

    def teardown_method(self):
        """Teardown after each test case is called."""
        del self.tcex

    #
    # Benchmark
    #

    @Benchmark()
    def test_benchmark(self):  # pylint: disable=no-self-use
        """Test benchmark decorator."""

    #
    # Debug
    #

    @Debug()
    def debug(self, arg1, arg2, kwarg1):  # pylint: disable=dangerous-default-value
        """Test debug decorator."""

    def test_debug(self):
        """Test debug decorator."""
        self.debug('arg1', 'arg2', kwarg1={'kwarg1': 'kwarg1'})

    #
    # FailOnInput
    #

    @FailOnInput(enable=True, values=[None], msg='pytest')
    def fail_on_input_enable(self, arg1):  # pylint: disable=no-self-use
        """Test fail on input decorator with no arg value (use first arg input)."""

    @FailOnInput(enable=True, values=[None], msg='pytest', arg='arg1')
    def fail_on_input_enable_with_arg(self, arg1):  # pylint: disable=no-self-use
        """Test fail on input decorator with no arg value (use first arg input)."""

    @FailOnInput(enable='fail_on_enabled', values=[None], msg='pytest')
    def fail_on_input_arg_enabled(self, arg1):  # pylint: disable=no-self-use
        """Test fail on input decorator with no arg value (use first arg input)."""

    @FailOnInput(enable='fail_on_disabled', values=[None], msg='pytest')
    def fail_on_input_arg_disabled(self, arg1):  # pylint: disable=no-self-use
        """Test fail on input decorator with no arg value (use first arg input)."""

    @FailOnInput(enable='fail_on_string', values=[None], msg='pytest')
    def fail_on_input_arg_string(self, arg1):  # pylint: disable=no-self-use
        """Test fail on input decorator with no arg value (use first arg input)."""

    def test_fail_on_input_enable_pass(self):
        """Test fail on input decorator."""
        self.fail_on_input_enable('pytest')

    def test_fail_on_input_enable_with_arg_pass(self):
        """Test fail on input decorator."""
        self.fail_on_input_enable_with_arg('pytest')

    def test_fail_on_input_fail(self):
        """Test fail on input decorator."""
        try:
            self.fail_on_input_enable(None)
            assert False, 'Fail on input did not catch null input.'
        except SystemExit:
            assert True

    def test_fail_on_input_arg_enable_pass(self):
        """Test fail on input decorator."""
        self.fail_on_input_arg_enabled('pytest')

    def test_fail_on_input_arg_disable_pass(self):
        """Test fail on input decorator."""
        self.fail_on_input_arg_disabled(None)
        assert True

    def test_fail_on_input_arg_string(self):
        """Test fail on input decorator."""
        try:
            self.fail_on_input_arg_string(None)
            assert False, 'Fail on input did not catch disabled arg.'
        except SystemExit:
            assert True

    #
    # FailOnOutput
    #

    @FailOnOutput(enable=True, values=[None], msg='pytest')
    def fail_on_output_enable(self):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        return True

    @FailOnOutput(enable=True, values=[None], msg='pytest')
    def fail_on_output_enable_fail(self):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        return None

    @FailOnOutput(enable=True, values=[None], msg='pytest')
    def fail_on_output_enable_list(self):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        return [True, False, True]

    @FailOnOutput(enable='fail_on_enabled', values=[None], msg='pytest')
    def fail_on_output_arg_enable(self):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        return True

    @FailOnOutput(enable='fail_on_string', values=[None], msg='pytest')
    def fail_on_output_arg_string(self):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        return True

    @FailOnOutput(enable=True, values=[None], msg='pytest')
    def fail_on_output_enable_list_fail(self):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        return [True, None, True]

    def test_fail_on_output_enable_pass(self):
        """Test fail on input decorator."""
        self.fail_on_output_enable()

    def test_fail_on_output_enable_fail(self):
        """Test fail on input decorator."""
        try:
            self.fail_on_output_enable_fail()
            assert False, 'Fail value not caught'
        except SystemExit:
            assert True

    def test_fail_on_output_enable_list_pass(self):
        """Test fail on input decorator."""
        self.fail_on_output_enable_list()
        assert True

    def test_fail_on_output_arg_enable_pass(self):
        """Test fail on input decorator."""
        self.fail_on_output_arg_enable()
        assert True

    def test_fail_on_output_arg_string_fail(self):
        """Test fail on input decorator."""
        try:
            self.fail_on_output_arg_string()
            assert False, 'String input for enabled not caught'
        except SystemExit:
            assert True

    def test_fail_on_output_arg_list_fail(self):
        """Test fail on input decorator."""
        try:
            self.fail_on_output_enable_list_fail()
            assert False, 'Fail value not caught'
        except SystemExit:
            assert True

    #
    # IterateOn
    #

    @IterateOnArg(arg='iterate_on')
    def iterate_on_pass(self, string):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        assert string == 'iterate_on'

    @IterateOnArg(arg='none', default='default')
    def iterate_on_pass_default(self, string):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        assert string == 'default'

    @IterateOnArg(arg='iterate_on', fail_on=['None'])
    def iterate_on_pass_fail_on(self, string):  # pylint: disable=no-self-use
        """Test fail on output decorator."""
        assert string == 'iterate_on'

    @IterateOnArg(arg='null', fail_on=['null'])
    def iterate_on_pass_fail_on_fail(self, string):  # pylint: disable=no-self-use
        """Test fail on output decorator."""

    def test_iterate_on_basic_pass(self):
        """Test iterate on decorator."""
        self.iterate_on_pass()  # pylint: disable=no-value-for-parameter
        assert True

    def test_iterate_on_default_pass(self):
        """Test iterate on decorator."""
        self.iterate_on_pass_default()  # pylint: disable=no-value-for-parameter
        assert True

    def test_iterate_on_fail_on_pass(self):
        """Test iterate on decorator."""
        self.iterate_on_pass_fail_on()  # pylint: disable=no-value-for-parameter
        assert True

    def test_iterate_on_fail_on_fail(self):
        """Test iterate on decorator."""
        try:
            self.iterate_on_pass_fail_on_fail()  # pylint: disable=no-value-for-parameter
            assert False, 'Fail on did not catch value.'
        except SystemExit:
            assert True

    #
    # OnException
    #

    @OnException(msg='This method failed')
    def on_exception_pass(self):  # pylint: disable=no-self-use
        """Test on exception decorator."""

    @OnException(msg='This method failed')
    def on_exception_fail(self):  # pylint: disable=no-self-use
        """Test on exception decorator."""
        raise RuntimeError('failed')

    def test_on_exception_pass(self):
        """Test on exception decorator."""
        self.on_exception_pass()
        assert True

    def test_on_exception_fail(self):
        """Test on exception decorator."""
        try:
            self.on_exception_fail()
            assert False, 'Decorator did not catch method exception'
        except SystemExit:
            assert True

    #
    # OnSuccess
    #

    @OnSuccess(msg='This method passed')
    def on_success_pass(self):  # pylint: disable=no-self-use
        """Test on exception decorator."""

    def test_on_success_pass(self):
        """Test on exception decorator."""
        self.on_success_pass()
        assert True
