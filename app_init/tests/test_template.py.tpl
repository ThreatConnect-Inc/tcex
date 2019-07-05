# -*- coding: utf-8 -*-
"""Test case template for App testing."""
import os
import sys

import pytest
from tcex.testing.monkeypatch import register_monkeypatch

${parent_import}
from .validate_feature import ValidateFeature  # pylint: disable=E0402

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)  # noqa: F821; pylint: disable=E0602
    sys.setdefaultencoding('utf-8')  # pylint: disable=no-member

# gather profile names
profiles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.d')
profile_names = []
for filename in sorted(os.listdir(profiles_dir)):
    if filename.endswith('.json'):
        profile_names.append(filename.replace('.json', ''))


# pylint: disable=W0235,too-many-function-args
class TestFeature(${parent_class}):
    """TcEx App Testing Template."""

    @classmethod
    def setup_class(cls):
        """Run setup logic before all test cases in this module."""
        super(TestFeature, cls).setup_class()

    def setup_method(self):
        """Run setup logic before test method runs."""
        super(TestFeature, self).setup_method()

    @classmethod
    def teardown_class(cls):
        """Run setup logic after all test cases in this module."""
        super(TestFeature, cls).teardown_class()

    def teardown_method(self):
        """Run teardown logic after test method completes."""
        super(TestFeature, self).teardown_method()

    @pytest.mark.parametrize('profile_name', profile_names)
    def test_profiles(self, profile_name, monkeypatch):
        """Run pre-created testing profiles."""
        pd = self.profile(profile_name)
        # uncomment to start using the monkey patch annotations
        # register_monkeypatch(monkeypatch, pd)
        if self.env.intersection(set(pd.get('environments', ['build']))):
            assert self.run_profile(profile_name) in pd.get('exit_codes', [0])
            ValidateFeature(self.validator).validate(pd.get('outputs'))
            ${validate_batch_method}
