# -*- coding: utf-8 -*-
'''Test the TcEx Threat Intel Module.'''

from tcex.testing import TestCasePlaybook
import pytest
from .validation import Validation  # pylint: disable=E0402

# pylint: disable=W0235,too-many-function-args


class TestFeature(TestCasePlaybook):
    """Test TcEx Host Indicators."""

    def setup_class(self):
        """Run setup logic before all test cases in this module."""
        super().setup_class(self)

    def setup_method(self):
        """Run setup logic before test method runs."""
        super().setup_method()

    def teardown_class(self):
        """Run setup logic after all test cases in this module."""
        super().teardown_class(self)

    def teardown_method(self):
        """Run teardown logic after test method completes."""
        super().teardown_method()

    @pytest.mark.parametrize('profile_name', ['test_profile'])
    def test_profiles(self, profile_name):
        """Unique_name should be the unique permutation name they pass in via the tctest command"""
        validator = Validation()
        self.run_profile(profile_name)
        validator.validation(self.profile(profile_name).get('outputs'))
