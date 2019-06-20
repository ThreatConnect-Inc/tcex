# -*- coding: utf-8 -*-
"""Test case template for App testing."""
import os
import pytest

from tcex.testing import TestCasePlaybook
from .validate_feature import ValidateFeature  # pylint: disable=E0402

# gather profile names
profiles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.d')
profile_names = []
for filename in sorted(os.listdir(profiles_dir)):
    if filename.endswith('.json'):
        profile_names.append(filename.replace('.json', ''))


# pylint: disable=W0235,too-many-function-args
class TestFeature(TestCasePlaybook):
    """TcEx App Testing Template."""

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

    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name):
        """Run pre-created testing profiles."""
        pd = self.profile(profile_name)
        if self.env.intersection(set(pd.get('environments', ['build']))):
            assert self.run_profile(profile_name) in pd.get('exit_codes', [0])
            ValidateFeature(self.validator).validate(pd.get('outputs'))
