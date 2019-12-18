# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""

from ..tcex_init import tcex
from tcex.case_management.tql import TQL


# pylint: disable=W0201
class TestArtifactIndicators:
    """Test TcEx Address Indicators."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def test_get_single(self):
        """
        Tests Artifact Get by Id
        """
        artifact = self.test_create(summary='asn4324', delete=False)
        self.test_create(summary='asn4442', delete=False)

        artifact = self.cm.artifact(id=artifact.id)
        artifact.get()
        assert artifact.summary == 'asn4324'

        self.test_delete('artifact_name', create=False)
        self.test_delete('artifact_name_2', create=False)

    def test_get_many(self):
        """Tests getting all artifacts"""
        artifact = self.cm.artifact()
        assert len(artifact) > 0

    def test_tql(self):
        """
        Tests Artifact Get by TQL's
        """
        artifact = self.test_create(summary='asn5433')
        self.test_create(summary='asn5432', case_id=1)
        self.test_create(summary='asn5434', case_id=1)
        self.test_create(summary='asn4566', type='Artifact 2', case_id=1)

        artifacts = self.cm.artifacts()
        artifacts.summary_filter(TQL.Operator.EQ, 'asn5433')
        assert len(artifacts) == 1
        for artifact in artifacts:
            assert artifact.summary == 'asn5433'
            assert artifact.type == 'New Artifact Type'

        artifacts.tql.filters = []

        artifacts.id_filter(TQL.Operator.EQ, artifact.id)
        assert len(artifacts) == 1
        for artifact in artifacts:
            assert artifact.summary == 'asn5433'
            assert artifact.type == 'New Artifact Type'

        artifacts.tql.filters = []

        artifacts.case_filter(TQL.Operator.EQ, 1)

    def test_delete(self, summary='artifact_name', create=True):
        """
        Tests Artifact Deletion
        """
        if create:
            self.test_create(summary, delete=False)
        artifacts = self.cm.artifacts()
        artifacts.summary_filter(TQL.Operator.EQ, summary)
        for artifact in artifacts:
            artifact.delete()

    def test_create(
        self,
        summary='asn4354',
        type='New Artifact Type',
        intel_type='ArtifactType intelType',
        case_id=None,
        delete=True,
    ):
        """
        Tests Artifact Creation
        """
        if not case_id:
            case = self.cm.case(name='artifact_name', status='Open', severity='Low')
            case.submit()
            case_id = case.id

        artifact = self.cm.artifact(
            summary=summary, type=type, intel_type=intel_type, case_id=case_id
        )
        artifact.submit()

        assert artifact.case_id == case_id
        assert artifact.summary == summary
        # assert artifact.intel_type == intel_type
        assert artifact.type == type

        if delete:
            self.test_delete(summary, create=False)

        return artifact
