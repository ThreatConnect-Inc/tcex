# -*- coding: utf-8 -*-
"""Test the TcEx Case Management Module."""
from tcex.case_management.tql import TQL

from ..tcex_init import tcex


class TestArtifactIndicators:
    """Test TcEx CM Artifact Interface."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm  # pylint: disable=attribute-defined-outside-init

    def test_get_single_by_id(self):
        """Tests Artifact Get by Id"""
        case_management_case_name = 'pytest-artifact-case'
        case_management_xid = 'pytest-artifact-case'
        artifact_summary = 'asn7654'

        # ensure case exist
        case = self.cm.case(
            name=case_management_case_name, status='Open', severity='Low', xid=case_management_xid
        )
        case.submit()

        # ensure artifact exist
        artifact = self.cm.artifact(
            case_id=case.id, intel_type='indicator-ASN', summary=artifact_summary, type='ASN',
        )
        artifact.submit()

        artifact = self.cm.artifact(id=artifact.id)
        artifact.get()

        # run assertions on returned data
        assert artifact.summary == artifact_summary

        # cleanup data from TC instance
        artifact.delete()
        case.delete()

    def test_get_many(self):
        """Tests getting all artifacts"""
        case_management_case_name = 'pytest-artifact-case'
        case_management_xid = 'pytest-artifact-case'
        artifact_summary = 'asn7654'

        # ensure case exist
        case = self.cm.case(
            name=case_management_case_name, status='Open', severity='Low', xid=case_management_xid
        )
        case.submit()

        # ensure artifact exist
        artifact = self.cm.artifact(
            case_id=case.id, intel_type='indicator-ASN', summary=artifact_summary, type='ASN',
        )
        artifact.submit()

        # iterate over all artifact looking for needle
        for a in self.cm.artifacts():
            if a.summary == artifact_summary:
                break
        else:
            assert False

        # cleanup data from TC instance
        artifact.delete()
        case.delete()

    def test_tql(self):
        """Tests Artifact Get by TQL's"""
        artifact = self.test_create(summary='asn5433')
        self.test_create(summary='asn5432', case_id=1)
        self.test_create(summary='asn5434', case_id=1)
        self.test_create(summary='asn4566', type_='Artifact 2', case_id=1)

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
        type_='New Artifact Type',
        intel_type='ArtifactType intelType',
        case_id=None,
        delete=True,
    ):
        """Tests Artifact Creation"""
        if not case_id:
            case = self.cm.case(name='artifact_name', status='Open', severity='Low')
            case.submit()
            case_id = case.id

        artifact = self.cm.artifact(
            summary=summary, type=type_, intel_type=intel_type, case_id=case_id
        )
        print(artifact)
        artifact.submit()

        # assert artifact.case_id == case_id
        # assert artifact.summary == summary
        # # assert artifact.intel_type == intel_type
        # assert artifact.type == type_

        if delete:
            self.test_delete(summary, create=False)

        return artifact
