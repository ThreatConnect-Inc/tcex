"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestIntelRequirements(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('intel_requirements')

    def test_intel_requirements_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_intel_requirements_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_intel_requirements_object_properties(self):
        """Test properties."""
        super().obj_properties()

    @pytest.mark.xfail(reason='Verify TC Version running against.')
    def test_intel_requirements_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()
