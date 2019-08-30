# -*- coding: utf-8 -*-
"""Test case template for App testing."""
# flake8: noqa: F401
import os
import sys

import pytest
from tcex.testing.monkeypatch import register_monkeypatches  # pylint: disable=W0611
from ..profiles import profiles

${parent_import}  # pylint: disable=C0411
from .validate_feature import ValidateFeature  # pylint: disable=E0402

# Python 2 unicode
if sys.version_info[0] == 2:
    reload(sys)  # noqa: F821; pylint: disable=E0602
    sys.setdefaultencoding('utf-8')  # pylint: disable=no-member

# get profile names
profile_names = profiles(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.d'))


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
    def test_profiles(self, profile_name, monkeypatch):  # pylint: disable=unused-argument
        """Run pre-created testing profiles."""
        pd = self.profile(profile_name)

        # uncomment to start using the monkey patch annotations
        # register_monkeypatches(monkeypatch, pd)

        assert self.run_profile(pd) in pd.get('exit_codes', [0])
        ValidateFeature(self.validator).validate(pd.get('outputs'))
        ${validate_batch_method}
