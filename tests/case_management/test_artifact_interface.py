# -*- coding: utf-8 -*-
"""Test the TcEx Case Management Module."""
import os
from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


class TestArtifactIndicators:
    """Test TcEx CM Artifact Interface."""

    cm = None
    cm_helper = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper(self.cm)

    def teardown_method(self):
        """Configure setup before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_create_by_case_id(self):
        """Test Artifact Creation"""

        # create case
        case = self.cm_helper.create_case(case_name=__name__)

        artifact_data = {
            'artifact_intel_type': 'indicator-ASN',
            'artifact_summary': 'asn7654',
            'artifact_type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(
            case_id=case.id,
            intel_type=artifact_data.get('artifact_intel_type'),
            summary=artifact_data.get('artifact_summary'),
            type=artifact_data.get('artifact_type'),
        )
        artifact.submit()

        # get single artifact by id
        artifact = self.cm.artifact(id=artifact.id)
        artifact.get()

        # run assertions on returned data
        assert artifact.intel_type == artifact_data.get('artifact_intel_type')
        assert artifact.summary == artifact_data.get('artifact_summary')
        assert artifact.type == artifact_data.get('artifact_type')

    def test_delete(self):
        """Test Artifact Deletion"""
        artifact_data = {
            'artifact_intel_type': 'indicator-ASN',
            'artifact_summary': 'asn7654',
            'artifact_type': 'ASN',
            'case_name': __name__,
            'case_xid': __name__,
        }

        # create artifact
        artifact = self.cm_helper.create_artifact(**artifact_data)

        # get single artifact by id
        artifact = self.cm.artifact(id=artifact.id)

        # delete the artifact
        artifact.delete()

        # test artifact is deleted
        try:
            artifact.get()
            assert False
        except Exception:
            pass

    def test_get_many(self):
        """Test Artifact Get Many"""
        artifact_data = {
            'artifact_intel_type': 'indicator-ASN',
            'artifact_summary': 'asn7654',
            'artifact_type': 'ASN',
            'case_name': __name__,
            'case_xid': __name__,
        }

        # create artifact
        self.cm_helper.create_artifact(**artifact_data)

        # iterate over all artifact looking for needle
        for a in self.cm.artifacts():
            if a.summary == artifact_data.get('artifact_summary'):
                break
        else:
            assert False

    def test_get_single_by_id(self):
        """Test Artifact Get by Id"""
        artifact_data = {
            'artifact_intel_type': 'indicator-ASN',
            'artifact_summary': 'asn7654',
            'artifact_type': 'ASN',
            'case_name': __name__,
            'case_xid': __name__,
        }

        # create artifact
        artifact = self.cm_helper.create_artifact(**artifact_data)

        # get single artifact by id
        artifact = self.cm.artifact(id=artifact.id)
        artifact.get()

        # run assertions on returned data
        assert artifact.intel_type == artifact_data.get('artifact_intel_type')
        assert artifact.summary == artifact_data.get('artifact_summary')
        assert artifact.type == artifact_data.get('artifact_type')

    def test_get_by_tql_filter_case_id(self):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case(case_name=__name__)

        # create artifact #1
        artifact_data = {
            'artifact_intel_type': 'indicator-ASN',
            'artifact_summary': 'asn7777',
            'artifact_type': 'ASN',
            'case_id': case.id,
        }
        artifact = self.cm_helper.create_artifact(**artifact_data)

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.case_id(TQL.Operator.EQ, case.id)

        assert len(artifacts.as_dict) == 1
        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('artifact_summary')
            assert artifact.type == artifact_data.get('artifact_type')

    def test_get_by_tql_filter_id(self):
        """Test Artifact Get by TQL"""
        # create artifact
        artifact_data = {
            'artifact_intel_type': 'indicator-ASN',
            'artifact_summary': 'asn7777',
            'artifact_type': 'ASN',
            'case_name': __name__,
            'case_xid': __name__,
        }
        artifact = self.cm_helper.create_artifact(**artifact_data)

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.id(TQL.Operator.EQ, artifact.id)

        assert len(artifacts.as_dict) == 1
        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('artifact_summary')
            assert artifact.type == artifact_data.get('artifact_type')

    def test_get_by_tql_filter_summary(self):
        """Test Artifact Get by TQL"""
        # create artifact #1
        artifact_data = {
            'artifact_intel_type': 'indicator-ASN',
            'artifact_summary': 'asn7777',
            'artifact_type': 'ASN',
            'case_name': __name__,
            'case_xid': __name__,
        }
        artifact = self.cm_helper.create_artifact(**artifact_data)

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.summary(TQL.Operator.EQ, artifact_data.get('artifact_summary'))

        assert len(artifacts.as_dict) == 1
        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('artifact_summary')
            assert artifact.type == artifact_data.get('artifact_type')
