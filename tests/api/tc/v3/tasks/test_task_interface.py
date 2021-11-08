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
from tests.api.tc.v3.v3_helpers import TestCaseManagement, V3Helper


class TestTasks(TestCaseManagement):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('tasks')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        # TODO: [med] @bpurdy - do you recall what the condition is for?
        # Ya - It was to make testing easier since we were manually verifying the objects were
        # created correctly and they kept getting deleted which was annoying.
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
        task.add_note(**note_data)

        # [Create Testing] add the artifact data to the object
        task.add_artifact(**artifact_data)

        # [Create Testing] submit the object to the TC API
        task.submit()

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
        assert len(artifacts) == 1, 'Artifact was not added/retrieved from task object.'
        for artifact in task.artifacts:
            # only a single artifact was added so summary should match
            assert artifact.model.summary == artifact_data.get('summary')

        # [Retrieve Testing] run assertions on the nested artifact data, which
        # is only available due to params being added to the get() method.
        assert task.model.artifacts.data[0].summary == artifact_data.get('summary')

        # [Retrieve Testing] run assertions on returned data
        assert task.as_entity == {'type': 'Task', 'id': task.model.id, 'value': task.model.name}
        assert task.required_properties  # coverage: required_properties
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
        task.add_note(**note_data)

        # [Create Testing] add the artifact data to the object
        task.add_artifact(**artifact_data)

        # [Create Testing] submit the object to the TC API
        task.submit()

        task.model.status = 'Closed'
        # TODO: [High] This is failing because the attributes inner object doesnt contain the
        #  `type` field. This is because the API endpoint for the attributes says its not
        #  `updatable` so its being excluded from PUTS.
        task.submit()
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
        # TODO: [Medium] Outstanding core bug relating to this filter
        # tasks.filter.case_severity(TqlOperator.EQ, case.model.severity)
        # tasks.filter.completed_by(TqlOperator.NE, None)

        for task in tasks:
            assert task.model.name == task_data.get('name')
            break
        else:
            assert False, f'No task found for tql -> {tasks.tql.as_str}'
