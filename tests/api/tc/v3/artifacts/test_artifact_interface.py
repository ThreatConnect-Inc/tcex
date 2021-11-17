"""Test the TcEx API Module."""
# standard library
import os
import time
from datetime import datetime, timedelta
from random import randint

# third-party
import pytest
from pytest import FixtureRequest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestArtifacts(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('artifacts')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        # Allows manual verification in the ThreatConnect Instance
        if os.getenv('TEARDOWN_METHOD') is None:
            self.v3_helper.cleanup()

    def test_artifact_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_artifact_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_artifact_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_artifact_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_artifact_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define object data
        artifact_data = {
            'case_id': case.model.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}

        # [Create Testing] create the object object
        artifact = self.v3.artifact(**artifact_data)

        # [Create Testing] add the note data to the object
        artifact.stage_note(note_data)

        # [Create Testing] create the object to the TC API
        artifact.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        artifact = self.v3.artifact(id=artifact.model.id)

        # [Retrieve Testing] get the object from the API
        artifact.get(params={'fields': 'notes'})

        # [Retrieve Testing] test "notes" method
        for note in artifact.notes:
            # only a single note was added so text should match
            assert note.model.text == note_data.get('text')

        # [Retrieve Testing] run assertions on the nested note data, which
        # is only available due to params being added to the get() method.
        assert artifact.model.notes.data[0].text == note_data.get('text')

        # [Retrieve Testing] run assertions on returned data
        assert artifact.model.intel_type == artifact_data.get('intel_type')
        assert artifact.model.summary == artifact_data.get('summary')
        assert artifact.model.type == artifact_data.get('type')
        assert artifact.model.field_name is None

    def test_artifact_all_filters_on_case(self, request: FixtureRequest):
        """Test TQL Filters for artifact on a Case"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define object data
        artifact_data = {
            'case_id': case.model.id,
            'intel_type': 'indicator-File',
            'source': 'tcex testing',
            'summary': '3BD214E8ACC29E123FE59CC14668407B0EEB1F2AA52E812E98874B7583EC7BDF',
            'type': 'File Hash',
        }

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}

        # [Create Testing] create the object
        artifact = self.v3.artifact(**artifact_data)

        # [Create Testing] add the note data to the object
        artifact.stage_note(note_data)

        # [Create Testing] create the object to the TC API
        artifact.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        artifact = self.v3.artifact(id=artifact.model.id)

        # [Retrieve Testing] get the object from the API
        artifact.get(params={'fields': 'notes'})
        note_id = artifact.model.notes.data[0].id

        # [Retrieve Testing] retrieve object using tql filters
        artifacts = self.v3.artifacts(params={'fields': 'analytics'})

        # [Filter Testing] analytics_score - This works, but
        #     the delay in the score updating takes to long
        # artifacts.filter.analytics_score(TqlOperator.GT, 50)

        # [Filter Testing] case_id
        artifacts.filter.case_id(TqlOperator.EQ, case.model.id)

        # [Filter Testing] date_added
        artifacts.filter.date_added(
            TqlOperator.GT, (datetime.utcnow() - timedelta(days=1)).isoformat()
        )

        # [Filter Testing] has_case - using id filter as it's easily available
        artifacts.filter.has_case.id(TqlOperator.EQ, case.model.id)

        # TODO: [PLAT-2830] not available via the API currently
        # [Filter Testing] has_group
        # artifacts.filter.has_group.id(TqlOperator.EQ, ???)

        # TODO: [PLAT-2830] not available via the API currently
        # [Filter Testing] has_indicator
        # artifacts.filter.has_indicator.id(TqlOperator.EQ, ???)

        # [Filter Testing] has_note - using <object>_id as it's easily available
        artifacts.filter.has_note.artifact_id(TqlOperator.EQ, artifact.model.id)

        # [Filter Testing] id
        artifacts.filter.id(TqlOperator.EQ, artifact.model.id)

        # TODO: [PLAT-2830] not available via the API currently
        # [Filter Testing] indicator_active
        # artifacts.filter.indicator_active(TqlOperator.EQ, True)

        # [Filter Testing] note_id - the note_id has to be retrieved first
        artifacts.filter.note_id(TqlOperator.EQ, note_id)

        # [Filter Testing] source
        artifacts.filter.source(TqlOperator.EQ, artifact_data.get('source'))

        # [Filter Testing] summary
        artifacts.filter.summary(TqlOperator.EQ, artifact_data.get('summary'))

        # [Filter Testing] type
        artifacts.filter.type(TqlOperator.EQ, artifact_data.get('type'))

        # [Filter Testing] type_name
        artifacts.filter.type_name(TqlOperator.EQ, artifact_data.get('type'))

        # [Retrieve Testing] get the object from the API
        for artifact in artifacts:
            assert artifact.model.summary == artifact_data.get('summary')
            break
        else:
            assert False, f'No artifact found for tql -> {artifacts.tql.as_str}'

    def test_artifact_all_filter_on_task(self, request: FixtureRequest):
        """Test TQL Filters for artifact on a Task"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define task data
        task_data = {
            'case_id': case.model.id,
            'name': f'name-{request.node.name}',
        }

        # [Create Testing] create the task object
        task = self.v3.task(**task_data)

        # [Create Testing] create the task ot the TC API
        task.create()

        # [Create Testing] define object data
        artifact_data = {
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'task_id': task.model.id,
            'type': 'ASN',
        }

        # [Create Testing] create the object object
        artifact = self.v3.artifact(**artifact_data)

        # [Create Testing] create the object ot the TC API
        artifact.create()

        # [Retrieve Testing] retrieve object using tql filters
        artifacts = self.v3.artifacts()

        # [Filter Testing] has_task -> using id since it's available
        artifacts.filter.has_task.id(TqlOperator.EQ, task.model.id)

        # [Filter Testing] task_id
        artifacts.filter.task_id(TqlOperator.EQ, task.model.id)

        # [Retrieve Testing] get the object from the API
        # print(f'TQL Filter -> ({artifacts.tql.as_str})')
        for artifact in artifacts:
            assert artifact.model.summary == artifact_data.get('summary')
            break
        else:
            assert False, f'No artifact found for tql -> {artifacts.tql.as_str}'

    def test_artifact_create_by_case_xid(self, request: FixtureRequest):
        """Test Artifact Creation"""
        # [Pre-Requisite] - create case and provide a unique xid
        case_xid = f'{request.node.name}-{time.time()}'
        _ = self.v3_helper.create_case(xid=case_xid)

        # [Create Testing] define object data
        artifact_data = {
            'case_xid': case_xid,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # [Create Testing] create the object
        artifact = self.v3.artifact(**artifact_data)

        # [Create Testing] create the object to the TC API
        artifact.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        artifact = self.v3.artifact(id=artifact.model.id)

        # [Retrieve Testing] get the object from the API
        artifact.get()

        # [Retrieve Testing] run assertions on returned data
        assert artifact.model.intel_type == artifact_data.get('intel_type')
        assert artifact.model.summary == artifact_data.get('summary')
        assert artifact.model.type == artifact_data.get('type')

    def test_artifact_delete_by_id(self):
        """Test Artifact Deletion"""
        # [Pre-Requisite] - create case and provide a unique xid
        case = self.v3_helper.create_case()

        # [Create Testing] define object data
        artifact_data = {
            'case_id': case.model.id,
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # [Create Testing] create the object
        artifact = self.v3.artifact(**artifact_data)

        # [Create Testing] create the object to the TC API
        artifact.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        artifact = self.v3.artifact(id=artifact.model.id)

        # [Delete Testing] remove the object
        artifact.delete()

        # [Delete Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            artifact.get()

        # [Delete Testing] assert error message contains the correct code
        # error -> "(952, 'Error during GET. API status code: 404, ..."
        assert '952' in str(exc_info.value)

    def test_artifact_get_many(self):
        """Test Artifact Get Many"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()
        artifact_count = 10
        artifact_ids = []
        for _ in range(0, artifact_count):
            # [Create Testing] define object data
            artifact_data = {
                'case_id': case.model.id,
                'intel_type': 'indicator-ASN',
                'summary': f'asn{randint(100, 999)}',
                'type': 'ASN',
            }

            # [Create Testing] create the object
            artifact = self.v3.artifact(**artifact_data)

            # [Create Testing] create the object to the TC API
            artifact.create()
            artifact_ids.append(artifact.model.id)

        # [Retrieve Testing] iterate over all object looking for needle
        artifacts = self.v3.artifacts(params={'resultLimit': 5})
        artifacts.filter.case_id(TqlOperator.EQ, case.model.id)
        for _, a in enumerate(artifacts):
            assert artifact.model.id in artifact_ids
            artifact_ids.remove(a.model.id)

        assert len(artifacts) == artifact_count
        assert not artifact_ids, 'Not all artifacts were returned.'

    def test_artifact_task_get_single_by_id_properties(self, request: FixtureRequest):
        """Test Artifact get single attached to task by id"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define task data
        task_data = {
            'case_id': case.model.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # [Create Testing] create the task object
        task = self.v3.task(**task_data)

        # [Create Testing] create the task ot the TC API
        task.create()

        # [Create Testing] define the object file data
        file_data = (
            'RmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )

        # [Create testing] define object data
        artifact_data = {
            'task_id': task.model.id,
            'task_xid': task.model.xid,
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': 'pytest test file artifact',
            'type': 'Certificate File',
            'note_text': 'artifact note text',
        }

        # [Create Testing] add the note data to the object
        artifact = self.v3.artifact()

        # [Create Testing] testing setters on model
        artifact.model.task_id = artifact_data.get('task_id')
        artifact.model.task_xid = artifact_data.get('task_xid')
        artifact.model.file_data = artifact_data.get('file_data')
        artifact.model.source = artifact_data.get('source')
        artifact.model.summary = artifact_data.get('summary')
        artifact.model.type = artifact_data.get('type')

        # [Create Testing] add the note data to the object
        note_data = {'text': artifact_data.get('note_text')}
        artifact.stage_note(note_data)

        # [Create Testing] create the object to the TC API
        artifact.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        artifact = self.v3.artifact(id=artifact.model.id)

        # [Retrieve Testing] get the object from the API
        artifact.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        assert artifact.model.case_id == case.model.id
        assert artifact.model.case_xid == case.model.xid
        assert artifact.model.file_data == file_data
        assert artifact.model.source == artifact_data.get('source')
        assert artifact.model.summary == artifact_data.get('summary')
        assert artifact.model.task.name == task.model.name
        assert artifact.model.task_id == task.model.id
        assert artifact.model.task_xid == task.model.xid
        assert artifact.model.intel_type is None
        assert artifact.model.type == artifact_data.get('type')
        for note in artifact.model.notes.data:
            if note.text == artifact_data.get('note_text'):
                break
            assert False, 'Note not found'

        # [Retrieve Testing] assert read-only data
        assert artifact.model.analytics_priority_level is None
        assert artifact.model.analytics_score is None
        assert artifact.model.analytics_type is None
        assert artifact.model.artifact_type.name == artifact_data.get('type')
        assert artifact.model.parent_case.id == case.model.id

        # [Retrieve Testing] test as_entity
        assert artifact.as_entity.get('value') == artifact_data.get('summary')

    def test_artifact_case_get_single_by_id_properties(self):
        """Test Artifact get single attached to case by id"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define the object file data
        file_data = (
            'RmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )

        # [Create Testing] define object data
        artifact_data = {
            'case_id': case.model.id,
            'case_xid': case.model.xid,
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': 'pytest test file artifact',
            'type': 'Certificate File',
            'note_text': 'artifact note text',
        }

        # [Create Testing] create the object
        artifact = self.v3.artifact()

        # [Create Testing] using model setters
        artifact.model.case_id = artifact_data.get('case_id')
        artifact.model.case_xid = artifact_data.get('case_xid')
        artifact.model.file_data = artifact_data.get('file_data')
        artifact.model.source = artifact_data.get('source')
        artifact.model.summary = artifact_data.get('summary')
        artifact.model.type = artifact_data.get('type')

        # [Create Testing] add the note data to the object
        notes = {'data': [{'text': artifact_data.get('note_text')}]}
        artifact.model.notes = notes

        # [Create Testing] create the object to the TC API
        artifact.create()

        # [Retrieve Testing] define the object with id filter,
        # using object id from the object created above
        artifact = self.v3.artifact(id=artifact.model.id)

        # [Retrieve Testing] get the object from the API
        artifact.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        assert artifact.model.case_id == artifact_data.get('case_id')
        assert artifact.model.case_xid == artifact_data.get('case_xid')
        assert artifact.model.file_data == file_data
        assert artifact.model.source == artifact_data.get('source')
        assert artifact.model.summary == artifact_data.get('summary')
        assert artifact.model.task_id is None
        assert artifact.model.task_xid is None
        assert artifact.model.intel_type is None
        assert artifact.model.type == artifact_data.get('type')
        for note in artifact.model.notes.data:  # Double check
            if note.text == artifact_data.get('note_text'):
                break
            assert False, 'Note not found'

        # [Retrieve Testing] run assertions on returned data
        assert artifact.model.analytics_priority_level is None
        assert artifact.model.analytics_score is None
        assert artifact.model.analytics_type is None
        assert artifact.model.artifact_type.name == artifact_data.get('type')
        assert artifact.model.parent_case.id == case.model.id

        # [Retrieve Testing] run assertions on returned data
        assert artifact.as_entity.get('value') == artifact_data.get('summary')

    def test_artifact_update_properties(self):
        """Test updating artifacts properties"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define the object file data
        file_data = (
            'FmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )

        # [Create Testing] define object data
        artifact_data = {
            'case_id': case.model.id,
            'file_data': f'{file_data}',
            'summary': f'asn{randint(100, 999)}',
            'type': 'Certificate File',
        }

        # [Create Testing] create the object
        artifact = self.v3.artifact(**artifact_data)

        # [Create Testing] create the object to the TC API
        artifact.create()

        # [Create Testing] define the object file data
        file_data = (
            'GmFpbGVkIHRvIGZpbmQgbGliIGRpcmVjdG9yeSAoWydsaWJfbGF0ZXN0JywgJ2xpYl8yLjcuMTUnXSkuCg=='
        )

        # [Create Testing] define object data
        artifact_data = {
            'source': 'artifact source',
            'file_data': f'{file_data}',
            'summary': f'asn{randint(100, 999)}',
        }

        # [Update Testing] update object properties
        artifact.model.source = artifact_data.get('source')
        artifact.model.summary = artifact_data.get('summary')
        artifact.model.file_data = artifact_data.get('file_data')

        # [Update Testing] update the object to the TC API
        artifact.update()

        # [Retrieve Testing] get the object from the API
        artifact.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        assert artifact.model.source == artifact_data.get('source')
        assert artifact.model.summary == artifact_data.get('summary')
        assert artifact.model.file_data == artifact_data.get('file_data')

    def test_artifact_get_by_tql_filter_fail_tql(self):
        """Test Artifact Get by TQL"""
        # retrieve object using TQL
        artifacts = self.v3.artifacts()
        artifacts.filter.tql = 'Invalid TQL'

        # [Fail Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            for _ in artifacts:
                pass

        # [Fail Testing] assert error message contains the correct code
        # error -> "(950, 'Error during pagination. API status code: 400, ..."
        assert '950' in str(exc_info.value)
        assert artifacts.request.status_code == 400
