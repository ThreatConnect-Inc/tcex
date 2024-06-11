"""TcEx Framework Module"""
# standard library
from collections.abc import Callable

# third-party
import pytest

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
        # assert ir.model.description == 'testing2'

    def test_associations(self):
        """Test associations."""
        ir = self.v3_helper.create_ir()
        # THIS DOES NOT WORK BECAUSE IT SENDS THE WRONG FIELDS VIA PUT!
        # indicator = self.v3_helper.create_indicator()
        # group = self.v3_helper.create_group()
        # case = self.v3_helper.create_case()
        # artifact = self.v3.artifact(
        #     **{
        #         'case_id': case.model.id,
        #         'intel_type': 'indicator-ASN',
        #         'summary': 'asn111',
        #         'type': 'ASN',
        #     }
        # )
        # artifact.create()
        #
        # ir.stage_associated_indicator(indicator)
        # ir.stage_associated_group(group)
        # ir.stage_associated_case(case)
        # ir.stage_associated_artifact(artifact)
        # ir.update()
        ir = self.v3.intel_requirement(id=ir.model.id)
        indicator = self.v3_helper.create_indicator()
        group = self.v3_helper.create_group()
        case = self.v3_helper.create_case()
        artifact = self.v3.artifact(
            **{
                'case_id': case.model.id,
                'intel_type': 'indicator-ASN',
                'summary': 'asn111',
                'type': 'ASN',
            }
        )
        artifact.create()

        ir.stage_associated_indicator(indicator)
        ir.stage_associated_group(group)
        ir.stage_associated_case(case)
        ir.stage_associated_artifact(artifact)
        ir.update()

        ir = self.v3.intel_requirement(id=ir.model.id)
        ir.get(
            params={
                'fields': [
                    'associatedArtifacts',
                    'associatedCases',
                    'associatedGroups',
                    'associatedIndicators',
                    'associatedVictimAssets',
                ]
            }
        )

        assert ir.model.associated_indicators.data[0].id == indicator.model.id
        assert ir.model.associated_groups.data[0].id == group.model.id
        assert ir.model.associated_cases.data[0].id == case.model.id
        assert ir.model.associated_artifacts.data[0].id == artifact.model.id

        for associated_indicator in ir.associated_indicators:
            assert indicator.model.id == associated_indicator.model.id

        for associated_group in ir.associated_groups:
            assert group.model.id == associated_group.model.id

        # TODO: Create a plat ticket for this
        # for associated_case in ir.associated_cases:
        #     assert case.model.id == associated_case.model.id

        # TODO: Create a plat ticket for this
        # for associated_artifact in ir.associated_artifacts:
        #     assert artifact.model.id == associated_artifact.model.id

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
