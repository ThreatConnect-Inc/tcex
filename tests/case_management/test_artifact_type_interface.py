# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from tcex.case_management.tql import TQL

from ..tcex_init import tcex


# pylint: disable=W0201
class TestArtifactTypeIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def test_get_single(self):
        """
        Tests Artifact Type Get by Id
        """
        artifact_type = self.cm.artifact_type(id=1)
        artifact_type.get()

        assert artifact_type.id == 1
        assert artifact_type.name == 'New Artifact Type'
        assert artifact_type.description == 'Random Description'
        assert artifact_type.data_type == 'String'
        assert artifact_type.intel_type == 'indicator-ASN'

    def test_get_many(self):
        """Tests getting all artifact types"""
        artifact_types = self.cm.artifact_types()
        assert len(artifact_types) == 3

    def test_tql(self):
        """
        Tests Artifact Type Get by TQL's
        """
        artifact_types = self.cm.artifact_types()

        # Test Name Filter
        artifact_types.name_filter(TQL.Operator.NE, 'New Artifact Type')
        assert len(artifact_types) == 2
        for artifact_type in artifact_types:
            assert artifact_type.id in [2, 3]

        # Test AND functionality
        artifact_types.data_type_filter(TQL.Operator.EQ, 'TimeStamp')
        assert len(artifact_types) == 1
        for artifact_type in artifact_types:
            assert artifact_type.id == 3
            assert artifact_type.name == 'Artifact 3'
            assert artifact_type.description == 'New Description'
            assert artifact_type.data_type == 'TimeStamp'
            assert artifact_type.intel_type is None

        # Clear Filters
        artifact_types.tql.filters = []

        artifact_types.active_filter(TQL.Operator.EQ, True)
        assert len(artifact_types) == 2
        for artifact_type in artifact_types:
            assert artifact_type.id in [1, 2]

        # Clear Filters
        artifact_types.tql.filters = []

        artifact_types.description_filter(TQL.Operator.CONTAINS, 'Random')
        assert len(artifact_types) == 1
        for artifact_type in artifact_types:
            assert artifact_type.id == 1
            assert artifact_type.name == 'New Artifact Type'
            assert artifact_type.description == 'Random Description'
            assert artifact_type.data_type == 'String'
            assert artifact_type.intel_type == 'indicator-ASN'
