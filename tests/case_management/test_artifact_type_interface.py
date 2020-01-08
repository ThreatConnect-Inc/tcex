# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
# from tcex.case_management.tql import TQL

from ..tcex_init import tcex


# pylint: disable=W0201
class TestArtifactTypeIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    # def test_get_single(self):
    #     """Tests Artifact Type Get by Id"""
    #     artifact_type = self.cm.artifact_type(id=1)
    #     artifact_type.get()

    #     assert artifact_type.id == 1
    #     assert artifact_type.name == 'E-mail Address'
    #     assert artifact_type.description == (
    #         'A name that identifies an electronic post office box on '
    #         'a network where Electronic-Mail (e-mail) can be sent.'
    #     )
    #     assert artifact_type.data_type == 'String'
    #     assert artifact_type.intel_type == 'indicator-EmailAddress'

    # def test_get_many(self):
    #     """Tests getting all artifact types"""
    #     artifact_types = self.cm.artifact_types()
    #     assert len(artifact_types.as_dict) >= 1

    # def test_tql(self):
    #     """Tests Artifact Type Get by TQL's"""
    #     artifact_types = self.cm.artifact_types()

    #     # Test Name Filter
    #     artifact_types.name_filter(TQL.Operator.EQ, 'ASN')
    #     assert len(artifact_types.as_dict) == 1

    #     for artifact_type in artifact_types:
    #         assert artifact_type.id == 7

    #     # Test AND functionality
    #     artifact_types.data_type_filter(TQL.Operator.EQ, 'String')
    #     assert len(artifact_types.as_dict) >= 1
    #     for artifact_type in artifact_types:
    #         assert artifact_type.data_type == 'String'

    #     # Clear Filters
    #     artifact_types.tql.filters = []

    #     artifact_types.active_filter(TQL.Operator.EQ, True)
    #     assert len(artifact_types.as_dict) >= 1
    #     # active field doesn't come back from API
    #     # for artifact_type in artifact_types:
    #     #     assert artifact_type.active == True

    #     # Clear Filters
    #     artifact_types.tql.filters = []

    #     artifact_types.description_filter(TQL.Operator.CONTAINS, 'Electronic-Mail')
    #     assert len(artifact_types.as_dict) >= 1
    #     for artifact_type in artifact_types:
    #         assert 'Electronic-Mail' in artifact_type.description
