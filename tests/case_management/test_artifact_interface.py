"""Test the TcEx Case Management Module."""
# standard library
import os
import time
from random import randint

# third-party
from dateutil.parser import parse

# first-party
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestArtifact(TestCaseManagement):
    """Test TcEx CM Artifact Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('artifact')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_artifact_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_artifact_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_artifact_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_artifact_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_artifact_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

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
        assert artifact.required_properties  # coverage: required_properties
        assert artifact.intel_type == artifact_data.get('intel_type')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.type == artifact_data.get('type')
        assert artifact.field_name is None

    def test_artifact_create_by_case_xid(self, request):
        """Test Artifact Creation"""
        # create case
        case_xid = f'{request.node.name}-{time.time()}'
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
        artifact.get()

        # delete the artifact
        artifact.delete()

        # test that artifact is deleted
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
        artifact.get(params={'result_limit': 10})

        # run assertions on returned data
        assert str(artifact)  # coverage: __str__ method
        assert artifact.intel_type == artifact_data.get('intel_type')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.type == artifact_data.get('type')

    def test_artifact_task_get_single_by_id_properties(self, request):
        """Test Artifact get single attached to task by id"""
        case = self.cm_helper.create_case()
        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        file_data = (
            'RmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )
        # task data
        artifact_data = {
            'task_id': task.id,
            'task_xid': task.xid,
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': 'pytest test file artifact',
            'type': 'Certificate File',
            'note_text': 'artifact note text',
        }

        # create task
        artifact = self.cm.artifact()

        # add properties
        artifact.task_id = artifact_data.get('task_id')
        artifact.task_xid = artifact_data.get('task_xid')
        artifact.file_data = artifact_data.get('file_data')
        artifact.source = artifact_data.get('source')
        artifact.summary = artifact_data.get('summary')
        artifact.type = artifact_data.get('type')

        # add note
        note_data = {'text': artifact_data.get('note_text')}
        artifact.add_note(**note_data)

        artifact.submit()

        # get task from API to use in asserts
        artifact = self.cm.artifact(id=artifact.id)
        artifact.get(all_available_fields=True)

        # run assertions on returned data
        assert artifact.case_id == case.id
        assert artifact.case_xid == case.xid
        assert artifact.file_data == file_data
        assert artifact.source == artifact_data.get('source')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.task.name == task.name
        assert artifact.task_id == task.id
        assert artifact.task_xid == task.xid
        assert artifact.intel_type is None
        assert artifact.type == artifact_data.get('type')
        for note in artifact.notes:
            if note.text == artifact_data.get('note_text'):
                break
            assert False, 'Note not found'

        # assert read-only data
        assert artifact.analytics_priority_level is None
        assert artifact.analytics_score is None
        assert artifact.analytics_type is None
        assert artifact.artifact_type.name == artifact_data.get('type')
        try:
            parse(artifact.date_added)
        except ValueError:
            assert False, 'Invalid date added'
        assert artifact.parent_case.id == case.id

        # test as_entity
        assert artifact.as_entity.get('value') == artifact_data.get('summary')

    def test_artifact_case_get_single_by_id_properties(self):
        """Test Artifact get single attached to case by id"""
        # create case
        case = self.cm_helper.create_case()

        file_data = (
            'RmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )
        # task data
        artifact_data = {
            'case_id': case.id,
            'case_xid': case.xid,
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': 'pytest test file artifact',
            'type': 'Certificate File',
            'note_text': 'artifact note text',
        }

        # create task
        artifact = self.cm.artifact()

        # add properties
        artifact.case_id = artifact_data.get('case_id')
        artifact.case_xid = artifact_data.get('case_xid')
        artifact.file_data = artifact_data.get('file_data')
        artifact.source = artifact_data.get('source')
        artifact.summary = artifact_data.get('summary')
        artifact.type = artifact_data.get('type')

        # add note
        notes = {'data': [{'text': artifact_data.get('note_text')}]}
        artifact.notes = notes

        artifact.submit()

        # get task from API to use in asserts
        artifact = self.cm.artifact(id=artifact.id)
        artifact.get(all_available_fields=True)

        # run assertions on returned data
        assert artifact.case_id == artifact_data.get('case_id')
        assert artifact.case_xid == artifact_data.get('case_xid')
        assert artifact.file_data == file_data
        assert artifact.source == artifact_data.get('source')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.task is None
        assert artifact.task_id is None
        assert artifact.task_xid is None
        assert artifact.intel_type is None
        assert artifact.type == artifact_data.get('type')
        for note in artifact.notes:
            if note.text == artifact_data.get('note_text'):
                break
            assert False, 'Note not found'

        # assert read-only data
        assert artifact.analytics_priority_level is None
        assert artifact.analytics_score is None
        assert artifact.analytics_type is None
        assert artifact.artifact_type.name == artifact_data.get('type')
        try:
            parse(artifact.date_added)
        except ValueError:
            assert False, 'Invalid date added'
        assert artifact.parent_case.id == case.id

        # test as_entity
        assert artifact.as_entity.get('value') == artifact_data.get('summary')

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

    def test_artifact_get_by_note_id_filter(self, request):
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

        note_data = {
            'text': f'note for artifact in {request.node.name}',
            'artifact_id': artifact.id,
        }

        # add a note to a artifact
        note = self.cm.note(**note_data)
        note.submit()

        artifacts = self.cm.artifacts()
        artifacts.filter.note_id(TQL.Operator.EQ, note.id)
        assert len(artifacts) == 1
        for artifact in artifacts:
            assert artifact.id == note_data.get('artifact_id')
            assert artifact.summary == artifact_data.get('summary')

    def test_artifact_get_by_has_case_filter_id(self):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data_1 = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }
        artifact_data_2 = {
            'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # create artifact
        artifact_1 = self.cm.artifact(**artifact_data_1)
        artifact_2 = self.cm.artifact(**artifact_data_2)
        artifact_1.submit()
        artifact_2.submit()

        artifacts = self.cm.artifacts()
        artifacts.filter.has_case.id(TQL.Operator.EQ, case.id)
        assert len(artifacts) == 2
        ids = [artifact_1.id, artifact_2.id]
        summaries = [artifact_1.summary, artifact_2.summary]
        for artifact in artifacts:
            assert artifact.id in ids
            assert artifact.summary in summaries
            ids.remove(artifact.id)
            summaries.remove(artifact.summary)

    def test_artifact_get_by_has_note_filter_id(self, request):
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

        note_data = {
            'text': f'note for artifact in {request.node.name}',
            'artifact_id': artifact.id,
        }

        # add a note to a artifact
        note = self.cm.note(**note_data)
        note.submit()

        artifacts = self.cm.artifacts()
        artifacts.filter.has_note.id(TQL.Operator.EQ, note.id)
        assert len(artifacts) == 1
        for artifact in artifacts:
            assert artifact.id == note_data.get('artifact_id')
            assert artifact.summary == artifact_data.get('summary')

    def test_artifact_get_by_has_task_filter_id(self, request):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        artifact_data = {
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
        }
        task = self.cm.task(**task_data)
        task.add_artifact(**artifact_data)
        task.submit()
        task.get(all_available_fields=True)
        artifact_id = None
        for artifact in task.artifacts:
            artifact_id = artifact.id
        artifacts = self.cm.artifacts()
        artifacts.filter.has_task.id(TQL.Operator.EQ, task.id)
        assert len(artifacts) == 1
        for artifact in artifacts:
            assert artifact.id == artifact_id
            assert artifact.summary == artifact_data.get('summary')

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

    # TODO: MJ working on this for AD-4631
    def test_artifact_get_by_tql_filter_task_id(self, request):
        """Test Artifact Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # artifact data
        artifact_data = {
            # 'case_id': case.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'task_id': task.id,
            'type': 'ASN',
        }

        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()

        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.case_id(TQL.Operator.EQ, case.id)
        artifacts.filter.task_id(TQL.Operator.EQ, task.id)

        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
            break
        else:
            assert False, 'No artifact returned for TQL'

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

        assert str(artifacts)  # coverage: __str__ method
        for artifact in artifacts:
            assert artifact.summary == artifact_data.get('summary')
            assert artifact.type == artifact_data.get('type')
            break
        else:
            assert False, 'No artifact returned for TQL'

    def test_artifact_update_properties(self):
        """Test updating artifacts properties"""
        case = self.cm_helper.create_case()

        file_data = (
            'FmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )
        # artifact data initially
        artifact_data = {
            'case_id': case.id,
            'file_data': f'{file_data}',
            'summary': f'asn{randint(100, 999)}',
            'type': 'Certificate File',
        }
        # create artifact
        artifact = self.cm.artifact(**artifact_data)
        artifact.submit()
        # artifact data updated
        file_data = (
            'GmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )
        # artifact data
        artifact_data = {
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': f'asn{randint(100, 999)}',
        }
        artifact.source = artifact_data.get('source')
        artifact.summary = artifact_data.get('summary')
        artifact.file_data = artifact_data.get('file_data')
        artifact.submit()
        artifact.get(all_available_fields=True)

        assert artifact.source == artifact_data.get('source')
        assert artifact.summary == artifact_data.get('summary')
        assert artifact.file_data == artifact_data.get('file_data')

    def test_artifact_get_by_tql_filter_fail_tql(self):
        """Test Artifact Get by TQL"""
        # retrieve artifacts using TQL
        artifacts = self.cm.artifacts()
        artifacts.filter.tql('Invalid TQL')

        try:
            for artifact in artifacts:  # pylint: disable=unused-variable
                pass
            assert False, 'TQL should have failed'
        except Exception:
            pass
