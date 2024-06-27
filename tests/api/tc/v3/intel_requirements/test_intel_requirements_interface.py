"""TcEx Framework Module"""
# standard library
from collections.abc import Callable

# third-party
import pytest

from tcex.api.tc.v3.intel_requirements.keyword_sections.keyword_section_model import \
    KeywordSectionModel
# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestIntelRequirements(TestV3):
    """Test TcEx API Interface."""

    v3_helper = V3Helper('intel_requirements')

    def setup_method(self, method: Callable):  # pylint: disable=arguments-differ
        """Configure setup before all tests."""
        super().setup_method()

        # remove any previous irs with the next test case name as a tag
        irs = self.tcex.api.tc.v3.intel_requirements()
        irs.filter.tag(TqlOperator.EQ, method.__name__)
        for ir in irs:
            ir.delete()

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

    def test_create_and_retrieve(self):
        """Test create and retrieve."""
        ir = self.v3_helper.create_ir(description='testing')
        assert ir.model.id is not None
        assert ir.model.description == 'testing'

        ir = self.v3.intel_requirement(id=ir.model.id)
        ir.model.description = 'testing2'
        ir.update()

        # ESUP-2521
        assert ir.model.description == 'testing2'

    def test_associations(self):
        """Test associations."""
        ir = self.v3_helper.create_ir()
        indicator = self.v3_helper.create_indicator()
        group = self.v3_helper.create_group()
        ir.stage_associated_indicator(indicator)
        ir.stage_associated_group(group)

        # ESUP-2532 : Associations not bi-directional
        # ir.stage_associated_case(case)
        # ir.stage_associated_artifact(artifact)
        # ir.stage_associated_victim_asset(asset)

        ir.update()

        # ir = self.v3.intel_requirement(id=ir.model.id)
        ir.get(params={'fields': ['_all_']})

        assert ir.model.associated_indicators.data[0].id == indicator.model.id
        assert ir.model.associated_groups.data[0].id == group.model.id

        for associated_indicator in ir.associated_indicators:
            assert indicator.model.id == associated_indicator.model.id

        for associated_group in ir.associated_groups:
            assert group.model.id == associated_group.model.id

    def test_keywords_section(self):
        """Test keywords section."""
        ir = self.v3_helper.create_ir()
        keyword_sections = [
            KeywordSectionModel(
                section_number=0,
                compare_value='includes',
                keywords=[{'value': 'keyword1'}]
            ),
            KeywordSectionModel(
                section_number=1,
                compare_value='includes',
                keywords=[{'value': 'keyword2'}]
            )
        ]
        ir.replace_keyword_section(keyword_sections)
        ir.update()
        ir = self.v3.intel_requirement(id=ir.model.id)
        ir.get()

        assert len(ir.model.keyword_sections) == 2
        # assert ir.model.keyword_sections[0].section_number == 0  # This doesnt come back
        assert ir.model.keyword_sections[0].compare_value == 'includes'
        assert ir.model.keyword_sections[0].keywords[0].get('value') == 'keyword1'
        # assert ir.model.keyword_sections[1].section_number == 1  # This doesnt come back
        assert ir.model.keyword_sections[1].compare_value == 'includes'
        assert ir.model.keyword_sections[1].keywords[0].get('value') == 'keyword2'

    def test_intel_requirement_get_many(self, count=10):
        """Test Intel Requirement Get Many."""
        ids = set()
        for _ in range(0, count):
            ir = self.v3_helper.create_ir()
            ids.add(ir.model.id)

        irs = self.v3.intel_requirements()
        irs.filter.id(TqlOperator.IN, list(ids))

        assert len(irs) == count
        for ir in irs:
            assert ir.model.id in ids
            ids.remove(ir.model.id)
        assert not ids, 'Not all ids were found in the response.'
