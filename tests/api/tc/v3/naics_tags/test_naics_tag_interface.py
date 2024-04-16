"""TcEx Framework Module"""

# third-party
import pytest

# first-party
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestNAICSTags(TestV3):
    """Test TcEx NAICS Tags."""

    v3_helper = V3Helper('cases')

    @pytest.mark.parametrize(
        'id_,output,default',
        [
            ('111110', 'NAICS: 111110 - Soybean Farming', None),
            ('11521', 'NAICS: 11521 - Support Activities for Animal Production', 'Unknown'),
            ('11522', None, None),
            ('11522', 'Unknown', 'Unknown'),
        ],
    )
    def test_get_by_id(self, id_: str, output: str, default: str | None):
        """Test get_by_id method."""
        naics_tag = self.v3_helper.tcex.api.tc.v3.naics_tags.get_by_id(id_, default=default)
        assert naics_tag == output

    @pytest.mark.parametrize(
        'id_,output,default',
        [
            ('111110', [
                'NAICS: 11 - Agriculture, Forestry, Fishing and Hunting',
                'NAICS: 111 - Crop Production',
                'NAICS: 1111 - Oilseed and Grain Farming',
                'NAICS: 11111 - Soybean Farming',
                'NAICS: 111110 - Soybean Farming',
            ], None),
            ('11521', [
                'NAICS: 11 - Agriculture, Forestry, Fishing and Hunting',
                'NAICS: 115 - Support Activities for Agriculture and Forestry',
                'NAICS: 1152 - Support Activities for Animal Production',
                'NAICS: 11521 - Support Activities for Animal Production'
            ], None),
            ('11522', None, None),
            ('11522', ['Unknown'], ['Unknown']),
        ],
    )
    def test_get_all_by_id(self, id_: str, output: list[str], default: list[str] | None):
        """Test get_all_by_id method."""
        naics_tag = self.v3_helper.tcex.api.tc.v3.naics_tags.get_all_by_id(id_, default=default)
        assert naics_tag == output

    def test_cached(self):
        """Test that naics_tags property is cached."""
        naics_tag = self.v3_helper.tcex.api.tc.v3.naics_tags
        assert id(naics_tag) == id(self.v3_helper.tcex.api.tc.v3.naics_tags)
