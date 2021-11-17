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


class TestTasks(TestV3):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('tasks')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    # TODO: @bpurdy - move this to parent class and clean up other test classes
    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.v3_helper.cleanup()

    def test_task_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_task_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_task_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_task_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_task_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
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

        artifact_data = {
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}

        # [Create Testing] create the object object
        task = self.v3.task(**task_data)

        # [Create Testing] add the note data to the object
        task.stage_note(note_data)

        # [Create Testing] add the artifact data to the object
        task.stage_artifact(artifact_data)

        # [Create Testing] create the object to the TC API
        task.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        task = self.v3.task(id=task.model.id)

        # [Retrieve Testing] get the object from the API
        task.get(params={'fields': ['notes', 'artifacts']})

        # [Retrieve Testing] test "notes" method
        notes = self.v3.notes()
        notes.filter.task_id(TqlOperator.EQ, task.model.id)
        assert len(notes) == 1, 'Note was not added/retrieved from task object.'
        for note in task.notes:
            # only a single note was added so text should match
            assert note.model.text == note_data.get('text')

        # [Retrieve Testing] run assertions on the nested note data, which
        # is only available due to params being added to the get() method.
        assert task.model.notes.data[0].text == note_data.get('text')

        # [Retrieve Testing] test "artifacts" method
        artifacts = self.v3.artifacts()
        artifacts.filter.task_id(TqlOperator.EQ, task.model.id)
        assert len(artifacts) == 1, 'Task was not added/retrieved from task object.'
        for artifact in task.artifacts:
            # only a single artifact was added so summary should match
            assert artifact.model.summary == artifact_data.get('summary')

        # [Retrieve Testing] run assertions on the nested artifact data, which
        # is only available due to params being added to the get() method.
        assert task.model.artifacts.data[0].summary == artifact_data.get('summary')

        # [Retrieve Testing] run assertions on returned data
        assert task.as_entity == {'type': 'Task', 'id': task.model.id, 'value': task.model.name}
        assert task.model.name == task_data.get('name')
        assert task.model.description == task_data.get('description')
        assert task.model.xid == task_data.get('xid')
        assert task.model.status == 'Open'
        assert task.model.workflow_phase == task_data.get('workflow_phase')
        assert task.model.workflow_step == task_data.get('workflow_step')
        assert task.model.required is False

    def test_task_all_filters(self, request: FixtureRequest):
        """Test TQL Filters for task on a Case"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        future_1 = datetime.now() + timedelta(days=10)
        future_1 = future_1.strftime('%Y-%m-%dT%H:%M:%S')
        future_2 = datetime.now() + timedelta(days=5)
        future_2 = future_2.strftime('%Y-%m-%dT%H:%M:%S')

        # [Create Testing] define task data
        task_data = {
            'case_id': case.model.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'completed_date': future_1,
            'due_date': future_2,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}
        artifact_data = {
            'intel_type': 'indicator-ASN',
            'summary': f'asn{randint(100, 999)}',
            'type': 'ASN',
        }

        # [Create Testing] create the object
        task = self.v3.task(**task_data)

        # [Create Testing] add the note data to the object
        task.stage_note(note_data)

        # [Create Testing] add the artifact data to the object
        task.stage_artifact(artifact_data)

        # [Create Testing] create the object to the TC API
        task.create()

        task.model.status = 'Closed'
        task.update()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        task = self.v3.task(id=task.model.id)

        # [Retrieve Testing] get the object from the API
        task.get(params={'fields': ['notes', 'artifacts']})
        note_id = task.model.notes.data[0].id
        artifact_id = task.model.artifacts.data[0].id

        # [Retrieve Testing] retrieve object using tql filters
        tasks = self.v3.tasks()

        # [Filter Testing] analytics_score - This works, but
        #     the delay in the score updating takes to long
        # tasks.filter.analytics_score(TqlOperator.GT, 50)

        # [Filter Testing] case_id
        tasks.filter.case_id(TqlOperator.EQ, case.model.id)
        tasks.filter.completed_date(TqlOperator.EQ, task_data.get('completed_date'))
        tasks.filter.due_date(TqlOperator.EQ, task_data.get('due_date'))
        tasks.filter.id(TqlOperator.EQ, task.model.id)
        tasks.filter.description(TqlOperator.EQ, task_data.get('description'))
        tasks.filter.status(TqlOperator.EQ, task.model.status)
        tasks.filter.workflow_phase(TqlOperator.EQ, task_data.get('workflow_phase'))
        tasks.filter.workflow_step(TqlOperator.EQ, task_data.get('workflow_step'))
        tasks.filter.xid(TqlOperator.EQ, task_data.get('xid'))
        tasks.filter.required(TqlOperator.EQ, False)
        tasks.filter.name(TqlOperator.EQ, task_data.get('name'))
        tasks.filter.has_case.id(TqlOperator.EQ, case.model.id)
        tasks.filter.has_artifact.id(TqlOperator.EQ, artifact_id)
        tasks.filter.has_note.id(TqlOperator.EQ, note_id)
        # TODO: [PLAT-????] Outstanding core bug relating to this filter
        # tasks.filter.case_severity(TqlOperator.EQ, case.model.severity)
        # tasks.filter.completed_by(TqlOperator.NE, None)

        for task in tasks:
            assert task.model.name == task_data.get('name')
            break
        else:
            assert False, f'No task found for tql -> {tasks.tql.as_str}'

    def test_task_get_by_tql_filter_fail_tql(self):
        """Test Task Get by TQL"""
        # retrieve object using TQL
        tasks = self.v3.tasks()
        tasks.filter.tql = 'Invalid TQL'

        # [Fail Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            for _ in tasks:
                pass

        # [Fail Testing] assert error message contains the correct code
        # error -> "(950, 'Error during pagination. API status code: 400, ..."
        assert '950' in str(exc_info.value)
        assert tasks.request.status_code == 400

    def test_task_create_by_case_xid(self, request: FixtureRequest):
        """Test Task Creation"""
        # [Pre-Requisite] - create case and provide a unique xid
        case_xid = f'{request.node.name}-{time.time()}'
        _ = self.v3_helper.create_case(xid=case_xid)

        # [Create Testing] define object data
        task_data = {
            'case_xid': case_xid,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # [Create Testing] create the object
        task = self.v3.task(**task_data)

        # [Create Testing] create the object to the TC API
        task.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        task = self.v3.task(id=task.model.id)

        # [Retrieve Testing] get the object from the API
        task.get()

        # [Retrieve Testing] run assertions on returned data
        assert task.as_entity == {'type': 'Task', 'id': task.model.id, 'value': task.model.name}
        assert task.model.name == task_data.get('name')
        assert task.model.description == task_data.get('description')
        assert task.model.xid == task_data.get('xid')
        assert task.model.status == 'Open'
        assert task.model.workflow_phase == task_data.get('workflow_phase')
        assert task.model.workflow_step == task_data.get('workflow_step')
        assert task.model.required is False

    def test_task_delete_by_id(self, request: FixtureRequest):
        """Test Task Deletion"""
        # [Pre-Requisite] - create case and provide a unique xid
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

        # [Create Testing] create the object
        task = self.v3.task(**task_data)

        # [Create Testing] create the object to the TC API
        task.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        task = self.v3.task(id=task.model.id)

        # [Delete Testing] remove the object
        task.delete()

        # [Delete Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            task.get()

        # [Delete Testing] assert error message contains the correct code
        # error -> "(952, 'Error during GET. API status code: 404, ..."
        assert '952' in str(exc_info.value)

    def test_task_get_many(self):
        """Test Task Get Many"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()
        task_count = 10
        task_ids = []
        for _ in range(0, task_count):
            # [Create Testing] define task data
            task_data = {
                'case_id': case.model.id,
                'description': 'a description from pytest test',
                'name': f'name-{randint(100, 999)}',
            }

            # [Create Testing] create the object
            task = self.v3.task(**task_data)

            # [Create Testing] create the object to the TC API
            task.create()
            task_ids.append(task.model.id)

        # [Retrieve Testing] iterate over all object looking for needle
        tasks = self.v3.tasks(params={'resultLimit': 5})
        tasks.filter.case_id(TqlOperator.EQ, case.model.id)
        for task in tasks:
            assert task.model.id in task_ids
            task_ids.remove(task.model.id)

        assert len(tasks) == task_count
        assert not task_ids, 'Not all tasks were returned.'

    def test_task_get_single_by_id_properties(self, request: FixtureRequest):
        """Test Task get single attached to task by id"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create a task which the main task is dependent on
        task_data = {
            'case_id': case.model.id,
            'description': 'a description from pytest test',
            'name': 'name-depended_task',
            'workflow_phase': 0,
            'workflow_step': 1,
        }
        task_2 = self.v3.task(**task_data)
        task_2.create()

        # [Pre-Requisite] - construct some timestamps in the future for completed and due by fields.
        future_1 = datetime.now() + timedelta(days=10)
        future_2 = datetime.now() + timedelta(days=5)

        # [Pre-Requisite] construct the artifacts model
        artifact_count = 10
        artifact_summaries = []
        artifact_data = {'data': []}
        for _ in range(0, artifact_count):
            # [Pre-Requisite] define artifact data
            summary = f'asn{randint(100, 999)}'
            artifact_data.get('data').append(
                {
                    'intel_type': 'indicator-ASN',
                    'summary': summary,
                    'type': 'ASN',
                    'note_text': 'artifact note text',
                }
            )
            artifact_summaries.append(summary)

        # [Pre-Requisite] construct the notes model
        note_count = 10
        notes_text = []
        note_data = {'data': []}
        for _ in range(0, note_count):
            # [Pre-Requisite] define note data
            text = f'sample note generated: {time.time()} for {request.node.name} test task.'
            note_data.get('data').append({'text': text})

            notes_text.append(text)

        assignee = {'type': 'User', 'data': {'userName': 'bpurdy@threatconnect.com'}}
        # [Create Testing] define task data
        task_data = {
            'case_id': case.model.id,
            'artifacts': artifact_data,
            'assignee': assignee,
            'completed_date': future_2,
            'dependent_on_id': task_2.model.id,
            'description': f'a description from {request.node.name}',
            'due_date': future_1,
            'name': f'name-{request.node.name}',
            'notes': note_data,
            'status': 'Pending',  # It is always pending because of the depended on task
            'required': False,
            'workflow_phase': 0,
        }

        # [Create Testing] add the note data to the object
        task = self.v3.task()

        # [Create Testing] testing setters on model
        task.model.artifacts = task_data.get('artifacts')
        task.model.assignee = task_data.get('assignee')
        task.model.case_id = task_data.get('case_id')
        task.model.dependent_on_id = task_data.get('dependent_on_id')
        task.model.description = task_data.get('description')
        task.model.due_date = task_data.get('due_date')
        task.model.completed_date = task_data.get('completed_date')
        task.model.name = task_data.get('name')
        task.model.notes = task_data.get('notes')
        task.model.required = task_data.get('required')
        task.model.status = task_data.get('status')
        task.model.workflow_phase = task_data.get('workflow_phase')

        # [Create Testing] create the object to the TC API
        task.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        task = self.v3.task(id=task.model.id)

        # [Retrieve Testing] get the object from the API
        task.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        assert task.model.case_id == case.model.id
        assert task.model.name == task_data.get('name')
        assert task.model.required == task_data.get('required')
        assert task.model.status == task_data.get('status')
        assert task.model.workflow_phase == task_data.get('workflow_phase')
        assert task.model.assignee.type == assignee.get('type')
        assert task.model.assignee.data.user_name == assignee.get('data').get('userName')
        for note in task.model.notes.data:
            assert note.text in notes_text
            notes_text.remove(note.text)
        assert not notes_text, 'Incorrect amount of notes were retrieved'
        for artifact in task.model.artifacts.data:
            assert artifact.summary in artifact_summaries
            artifact_summaries.remove(artifact.summary)
        assert not artifact_summaries, 'Incorrect amount of artifacts were retrieved'

    def test_task_update_properties(self, request: FixtureRequest):
        """Test updating artifacts properties"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] define assignee data
        assignee = {'type': 'User', 'data': {'userName': 'bpurdy@threatconnect.com'}}

        # [Pre-Requisite] - create a task which the main task is dependent on
        task_data = {
            'assignee': assignee,
            'case_id': case.model.id,
            'description': 'a description from pytest test',
            'name': 'name-depended_task',
        }
        task = self.v3.task(**task_data)
        task.create()

        # This was tested locally since no Groups are on the system by default
        assignee = {'type': 'Group', 'data': {'name': 'temp_user_group'}}

        # [Update Testing] update object properties
        task_data = {
            # 'assignee': assignee,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
        }

        # task.model.assignee = assignee
        task.model.description = task_data.get('description')
        task.model.name = task_data.get('name')

        # [Update Testing] update the object to the TC API
        task.update()

        # [Retrieve Testing] get the object from the API
        task.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        # assert task.model.assignee.type == assignee.get('type')
        # assert task.model.assignee.data.user_name == assignee.get('data').get('userName')
        assert task.model.description == task_data.get('description')
        assert task.model.name == task_data.get('name')
