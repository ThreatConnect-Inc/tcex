"""TcEx Framework Module"""


import pytest

from tcex.pleb.cached_property_filesystem import cached_property_filesystem
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestMitreTags(TestV3):
    """Test TcEx Mitre Tags."""

    v3_helper = V3Helper('cases')

    # def teardown_method(self):
    #     """Clear the filesystem and in-memory caches after each test."""
    #     cached_property_filesystem._reset()

    @pytest.mark.parametrize(
        'mitre_id,output',
        [
            ('T1205.001', 'T1205.001 - Traffic Signaling: Port Knocking'),
            ('T1205', 'T1205 - Traffic Signaling'),
            ('T9999', 'T9999'),
        ],
    )
    def test_get_by_id(self, mitre_id: str, output: str):
        """Test get_by_id method."""
        mitre_tag = self.v3_helper.tcex.api.tc.v3.mitre_tags.get_by_id(mitre_id, default=mitre_id)
        assert mitre_tag == output

    @pytest.mark.parametrize(
        'name,output',
        [
            ('Port Knocking', 'T1205.001 - Traffic Signaling: Port Knocking'),
            ('Traffic Signaling', 'T1205 - Traffic Signaling'),
            ('Name Not Found', None),
            ('T1205.001', None),
        ],
    )
    def test_get_by_name(self, name: str, output: str | None):
        """Test get_by_name method."""
        mitre_tag = self.v3_helper.tcex.api.tc.v3.mitre_tags.get_by_name(name)
        assert mitre_tag == output

    @pytest.mark.parametrize(
        'value,output',
        [
            ('ID T1205.001 in middle', 'T1205.001 - Traffic Signaling: Port Knocking'),
            ('ID T1205 in middle', 'T1205 - Traffic Signaling'),
            ('T1205.001 in beginning', 'T1205.001 - Traffic Signaling: Port Knocking'),
            ('T1205 in beginning', 'T1205 - Traffic Signaling'),
            ('ID at end T1205.001', 'T1205.001 - Traffic Signaling: Port Knocking'),
            ('ID at end T1205', 'T1205 - Traffic Signaling'),
            ('T1205.001', 'T1205.001 - Traffic Signaling: Port Knocking'),
            ('T1205', 'T1205 - Traffic Signaling'),
            ('T1205 and T1205.001', None),
            ('T1205.001 and T1205', None),
            ('', None),
            ('No id in string', None),
            ('Invalid ID in string T99999', None),
        ],
    )
    def test_get_by_regex(self, value: str, output: str | None):
        """Test get_by_regex method."""
        mitre_tag = self.v3_helper.tcex.api.tc.v3.mitre_tags.get_by_id_regex(value)
        assert mitre_tag == output, f'mitre-tag: {mitre_tag} != {output}'
