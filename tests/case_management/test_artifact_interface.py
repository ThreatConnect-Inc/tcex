# -*- coding: utf-8 -*-
"""Test the TcEx Case Management Module."""
import os
import time
from random import randint
from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


class TestArtifact:
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
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_artifact_create_by_case_id(self):
        """Test Artifact Creation"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # get artifact from API to use in asserts
        artifact = self.cm.artifact(id=artifact.id)
        artifact.get()

        # run assertions on returned data
        assert artifact.intel_type == artifact_data.get('intel_type')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.type == artifact_data.get('type')

    def test_artifact_create_by_case_xid(self, request):
        """Test Artifact Creation"""
        # create case
        case_xid = case_xid = f'{request.node.name}-{time.time()}'
        self.cm_helper.create_case(xid=case_xid)

        # artifact data
        artifact_data = {
            'case_xid': case_xid,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # get single artifact by id
        artifact = self.cm.artifact(id=artifact.id)
        artifact.get()

        # run assertions on returned data
        assert artifact.intel_type == artifact_data.get('intel_type')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.type == artifact_data.get('type')

    def test_artifact_delete_by_id(self):
        """Test Artifact Deletion"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # get single artifact by id
        artifact = self.cm.artifact(id=artifact.id)

        # delete the artifact
        artifact.delete()

        # test artifact is deleted
        try:
            artifact.get()
            assert False
        except RuntimeError:
            pass

    def test_artifact_get_many(self):
        """Test Artifact Get Many"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # iterate over all artifact looking for needle
        for a in self.cm.artifacts():
            if a.summary == artifact_data.get('summary'):
                assert artifact.intel_type == artifact_data.get('intel_type')
                assert artifact.type == artifact_data.get('type')
                break
        else:
            assert False

    def test_artifact_get_single_by_id(self):
        """Test Artifact Get by Id"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # get single artifact by id
        artifact = self.cm.artifact(id=artifact.id)
        artifact.get()

        # run assertions on returned data
        assert artifact.intel_type == artifact_data.get('intel_type')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.type == artifact_data.get('type')

    def test_artifact_get_by_tql_filter_case_id(self):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.case_id(TQL.Operator.EQ, case.id)

        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
            break
        else:
            assert False, 'No artifact returned for TQL'

    # TODO: checking with MJ on what this should be
    def test_artifact_get_by_tql_filter_comment_id(self):
        """Test Artifact Get by TQL"""

    def test_artifact_get_by_tql_filter_id(self):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.id(TQL.Operator.EQ, artifact.id)

        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
            break
        else:
            assert False, 'No artifact returned for TQL'

    # TODO: this needs some consideration
    def test_artifact_get_by_tql_filter_hascase(self):
        """Test Artifact Get by TQL"""

    def test_artifact_get_by_tql_filter_source(self):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'source': 'pytest',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.case_id(TQL.Operator.EQ, case.id)
        artifacts.filter.source(TQL.Operator.EQ, artifact_data.get('source'))

        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
            break
        else:
            assert False, 'No artifact returned for TQL'

    def test_artifact_get_by_tql_filter_summary(self):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.case_id(TQL.Operator.EQ, case.id)
        artifacts.filter.summary(TQL.Operator.EQ, artifact_data.get('summary'))

        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
            break
        else:
            assert False, 'No artifact returned for TQL'

    # def test_artifact_get_by_tql_filter_task_id(self, request):
    #     """Test Artifact Get by TQL"""
    #     # create case
    #     case = self.cm_helper.create_case()

    #     # task data
    #     task_data = {
    #         'case_id': case.id,
    #         'name': f'name-{request.node.name}',
    #     }

    #     # create task
    #     task = self.cm.task(**task_data)
    #     task.submit()

    #     # artifact data
    #     artifact_data = {
    #         'case_id': case.id,
    #         'intel_type': 'indicator-ASN',
    #         'summary': f'asn{randint(100, 999)}',
    #         'task_id': task.id,
    #         'type': 'ASN',
    #     }

    #     # create artifact
    #     artifact = self.cm.artifact(**artifact_data)
    #     artifact.submit()

    #     # retrieve artifacts using TQL
    #     artifacts = self.cm.artifacts()
    #     artifacts.filter.case_id(TQL.Operator.EQ, case.id)
    #     artifacts.filter.task_id(TQL.Operator.EQ, task.id)

    #     for artifact in artifacts:
    #         assert artifact.summary == artifact_data.get('summary')
    #         assert artifact.type == artifact_data.get('type')
    #         break
    #     else:
    #         assert False, 'No artifact returned for TQL'

    def test_artifact_get_by_tql_filter_type_name(self):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.case_id(TQL.Operator.EQ, case.id)
        artifacts.filter.type_name(TQL.Operator.EQ, artifact_data.get('type'))

        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
            break
        else:
            assert False, 'No artifact returned for TQL'
