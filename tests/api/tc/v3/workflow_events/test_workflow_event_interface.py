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


class TestWorkflowEvents(TestCaseManagement):
    """Test TcEx API Interface."""

    v3 = None

    def setup_method(self):
        """Configure setup before all tests."""
        print('')  # ensure any following print statements will be on new line
        self.v3_helper = V3Helper('workflow_events')
        self.v3 = self.v3_helper.v3
        self.tcex = self.v3_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.v3_helper.cleanup()

    def test_workflow_event_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_workflow_event_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_workflow_event_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_workflow_event_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_workflow_event_create_and_retrieve_nested_types(self, request: FixtureRequest):
        """Test Object Creation

        A single test case to hit all sub-type creation (e.g., Notes).
        """
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_id': case.model.id,
            'summary': request.node.name,
        }

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}

        # [Create Testing] create the object object
        workflow_event = self.v3.workflow_event(**workflow_event_data)

        # [Create Testing] add the note data to the object
        workflow_event.add_note(**note_data)

        # [Create Testing] submit the object to the TC API
        workflow_event.submit()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        workflow_event = self.v3.workflow_event(id=workflow_event.model.id)

        # [Retrieve Testing] get the object from the API
        workflow_event.get(params={'fields': ['notes']})

        # [Retrieve Testing] test "notes" method
        notes = self.v3.notes()
        notes.filter.workflow_event_id(TqlOperator.EQ, workflow_event.model.id)
        assert len(notes) == 1, 'Note was not added/retrieved from workflow_event object.'
        for note in workflow_event.notes:
            # only a single note was added so text should match
            assert note.model.text == note_data.get('text')

    def test_workflow_event_all_filters(self, request: FixtureRequest):
        """Test TQL Filters for workflow_event on a Case"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create datetime in the past
        past = (datetime.now() - timedelta(days=10))

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_id': case.model.id,
            'summary': request.node.name,
            'event_date': past
        }

        # [Create Testing] define nested note data
        note_data = {'text': f'sample note for {request.node.name} test case.'}

        # [Create Testing] create the object object
        workflow_event = self.v3.workflow_event(**workflow_event_data)

        # [Create Testing] add the note data to the object
        workflow_event.add_note(**note_data)

        # [Create Testing] submit the object to the TC API
        workflow_event.submit()

        # [Retrieving Testing] Retrieving the workflow event to ensure the user object is populated
        workflow_event.get(all_available_fields=True)

        # [Filter Testing] create the object collection
        workflow_events = self.v3.workflow_events()

        workflow_events.filter.case_id(TqlOperator.EQ, case.model.id)
        workflow_events.filter.date_added(TqlOperator.GT, past)
        workflow_events.filter.deleted(TqlOperator.EQ, False)
        workflow_events.filter.event_date(TqlOperator.GT, past)
        workflow_events.filter.id(TqlOperator.EQ, workflow_event.model.id)
        # TODO: No link is generated/returned if workflow event is created via the api.
        # workflow_events.filter.link(TqlOperator.EQ, workflow_event.model.link)
        workflow_events.filter.summary(TqlOperator.EQ, workflow_event_data.get('summary'))
        workflow_events.filter.system_generated(TqlOperator.EQ, False)
        workflow_events.filter.user_name(TqlOperator.EQ, '22222222222222222222')
        # TODO: This filter does not work appropriatly.
        # workflow_events.filter.deleted_reason(TqlOperator.NE, 'This event has been deleted')
        for workflow_event in workflow_events:
            assert workflow_event.model.summary == workflow_event_data.get('summary')
            break
        else:
            assert False, f'No workflow_event found for tql -> {workflow_events.tql.as_str}'

    def test_workflow_event_get_by_tql_filter_fail_tql(self):
        """Test WorkflowEvent Get by TQL"""
        # retrieve object using TQL
        workflow_events = self.v3.workflow_events()
        workflow_events.filter.tql = 'Invalid TQL'

        # [Fail Testing] validate the object is removed
        with pytest.raises(RuntimeError) as exc_info:
            for _ in workflow_events:
                pass

        # [Fail Testing] assert error message contains the correct code
        # error -> "(950, 'Error during pagination. API status code: 400, ..."
        assert '950' in str(exc_info.value)
        assert workflow_events.request.status_code == 400

    def test_workflow_event_create_by_case_xid(self, request: FixtureRequest):
        """Test WorkflowEvent Creation"""
        # [Pre-Requisite] - create case and provide a unique xid
        case_xid = f'{request.node.name}-{time.time()}'
        _ = self.v3_helper.create_case(xid=case_xid)

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_xid': case_xid,
            'summary': request.node.name,
        }

        # [Create Testing] create the object
        workflow_event = self.v3.workflow_event(**workflow_event_data)

        # [Create Testing] submit the object to the TC API
        workflow_event.submit()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        workflow_event = self.v3.workflow_event(id=workflow_event.model.id)

        # [Retrieve Testing] get the object from the API
        workflow_event.get()

        # [Retrieve Testing] run assertions on returned data
        assert workflow_event.model.case_xid == case_xid

    def test_workflow_event_delete_by_id(self, request: FixtureRequest):
        """Test WorkflowEvent Deletion"""
        # [Pre-Requisite] - create case and provide a unique xid
        case = self.v3_helper.create_case()

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_id': case.model.id,
            'summary': request.node.name,
        }

        # [Create Testing] create the object
        workflow_event = self.v3.workflow_event(**workflow_event_data)

        # [Create Testing] submit the object to the TC API
        workflow_event.submit()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        workflow_event = self.v3.workflow_event(id=workflow_event.model.id)

        workflow_event.model.deleted_reason = 'Pytesting'

        # [Delete Testing] remove the object
        workflow_event.delete()

        workflow_event.get()

        assert workflow_event.model.deleted
        assert workflow_event.model.deleted_reason == 'Pytesting'

    def test_workflow_event_get_many(self):
        """Test WorkflowEvent Get Many"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()
        workflow_event_count = 10
        workflow_event_ids = []
        for _ in range(0, workflow_event_count):
            # [Create Testing] define workflow_event data
            workflow_event_data = {
                'case_id': case.model.id,
                'description': f'a description from pytest test',
                'name': f'name-{randint(100, 999)}',
            }

            # [Create Testing] create the object
            workflow_event = self.v3.workflow_event(**workflow_event_data)

            # [Create Testing] submit the object to the TC API
            workflow_event.submit()
            workflow_event_ids.append(workflow_event.model.id)

        # [Retrieve Testing] iterate over all object looking for needle
        workflow_events = self.v3.workflow_events(params={'resultLimit': 5})
        workflow_events.filter.case_id(TqlOperator.EQ, case.model.id)
        for workflow_event in workflow_events:
            assert workflow_event.model.id in workflow_event_ids
            workflow_event_ids.remove(workflow_event.model.id)

        assert len(workflow_events) == workflow_event_count
        assert not workflow_event_ids, 'Not all workflow_events were returned.'

    # def test_workflow_event_get_single_by_id_properties(self, request: FixtureRequest):
    #     """Test WorkflowEvent get single attached to workflow_event by id"""
    #     # [Pre-Requisite] - create case
    #     case = self.v3_helper.create_case()
    #
    #     # [Pre-Requisite] - create a workflow_event which the main workflow_event is dependent on
    #     workflow_event_data = {
    #         'case_id': case.model.id,
    #         'description': f'a description from pytest test',
    #         'name': f'name-depended_workflow_event',
    #         'workflow_phase': 0,
    #         'workflow_step': 1,
    #     }
    #     workflow_event_2 = self.v3.workflow_event(**workflow_event_data)
    #     workflow_event_2.submit()
    #
    #     # [Pre-Requisite] - construct some timestamps in the future for completed and due by fields.
    #     future_1 = (datetime.now() + timedelta(days=10))
    #     future_2 = datetime.now() + timedelta(days=5)
    #
    #     # [Pre-Requisite] construct the artifacts model
    #     artifact_count = 10
    #     artifact_summaries = []
    #     artifact_data = {'data': []}
    #     for _ in range(0, artifact_count):
    #         # [Pre-Requisite] define artifact data
    #         summary = f'asn{randint(100, 999)}'
    #         artifact_data.get('data').append(
    #             {
    #                 'intel_type': 'indicator-ASN',
    #                 'summary': summary,
    #                 'type': 'ASN',
    #                 'note_text': 'artifact note text',
    #             }
    #         )
    #         artifact_summaries.append(summary)
    #
    #     # [Pre-Requisite] construct the notes model
    #     note_count = 10
    #     notes_text = []
    #     note_data = {'data': []}
    #     for _ in range(0, note_count):
    #         # [Pre-Requisite] define note data
    #         text = f'sample note generated: {time.time()} for {request.node.name} test workflow_event.'
    #         note_data.get('data').append({'text': text})
    #
    #         notes_text.append(text)
    #
    #     # [Pre-Requisite] define assignee data
    #     assignee = {
    #         "type": "User",
    #         "data": {
    #             "user_name": "bpurdy@threatconnect.com"
    #         }
    #     }
    #
    #     # [Create Testing] define workflow_event data
    #     workflow_event_data = {
    #         'case_id': case.model.id,
    #         'artifacts': artifact_data,
    #         'assignee': assignee,
    #         'completed_date': future_2,
    #         'dependent_on_id': workflow_event_2.model.id,
    #         'description': f'a description from {request.node.name}',
    #         'due_date': future_1,
    #         'name': f'name-{request.node.name}',
    #         'notes': note_data,
    #         'status': 'Pending',  # It is always pending because of the depended on workflow_event
    #         'required': False,
    #         'workflow_phase': 0
    #     }
    #
    #     # [Create Testing] add the note data to the object
    #     workflow_event = self.v3.workflow_event()
    #
    #     # [Create Testing] testing setters on model
    #     workflow_event.model.artifacts = workflow_event_data.get('artifacts')
    #     workflow_event.model.assignee = workflow_event_data.get('assignee')
    #     workflow_event.model.case_id = workflow_event_data.get('case_id')
    #     workflow_event.model.dependent_on_id = workflow_event_data.get('dependent_on_id')
    #     workflow_event.model.description = workflow_event_data.get('description')
    #     workflow_event.model.due_date = workflow_event_data.get('due_date')
    #     workflow_event.model.completed_date = workflow_event_data.get('completed_date')
    #     workflow_event.model.name = workflow_event_data.get('name')
    #     workflow_event.model.notes = workflow_event_data.get('notes')
    #     workflow_event.model.required = workflow_event_data.get('required')
    #     workflow_event.model.status = workflow_event_data.get('status')
    #     workflow_event.model.workflow_phase = workflow_event_data.get('workflow_phase')
    #
    #     # [Create Testing] submit the object to the TC API
    #     workflow_event.submit()
    #
    #     # [Retrieve Testing] create the object with id filter,
    #     # using object id from the object created above
    #     workflow_event = self.v3.workflow_event(id=workflow_event.model.id)
    #
    #     # [Retrieve Testing] get the object from the API
    #     workflow_event.get(all_available_fields=True)
    #
    #     # [Retrieve Testing] run assertions on returned data
    #     assert workflow_event.model.case_id == case.model.id
    #     assert workflow_event.model.name == workflow_event_data.get('name')
    #     assert workflow_event.model.required == workflow_event_data.get('required')
    #     assert workflow_event.model.status == workflow_event_data.get('status')
    #     assert workflow_event.model.workflow_phase == workflow_event_data.get('workflow_phase')
    #     assert workflow_event.model.assignee.type == assignee.get('type')
    #     assert workflow_event.model.assignee.data.user_name == assignee.get('data').get('user_name')
    #     for note in workflow_event.model.notes.data:
    #         assert note.text in notes_text
    #         notes_text.remove(note.text)
    #     assert not notes_text, 'Incorrect amount of notes were retrieved'
    #     for artifact in workflow_event.model.artifacts.data:
    #         assert artifact.summary in artifact_summaries
    #         artifact_summaries.remove(artifact.summary)
    #     assert not artifact_summaries, 'Incorrect amount of artifacts were retrieved'
    #
    # def test_workflow_event_update_properties(self, request: FixtureRequest):
    #     """Test updating artifacts properties"""
    #     # [Pre-Requisite] - create case
    #     case = self.v3_helper.create_case()
    #
    #     # [Pre-Requisite] define assignee data
    #     assignee = {
    #         "type": "User",
    #         "data": {
    #             "user_name": "bpurdy@threatconnect.com"
    #         }
    #     }
    #
    #     # [Pre-Requisite] - create a workflow_event which the main workflow_event is dependent on
    #     workflow_event_data = {
    #         'assignee': assignee,
    #         'case_id': case.model.id,
    #         'description': f'a description from pytest test',
    #         'name': f'name-depended_workflow_event',
    #     }
    #     workflow_event = self.v3.workflow_event(**workflow_event_data)
    #     workflow_event.submit()
    #
    #     # This was tested locally since no Groups are on the system by default
    #     assignee = {
    #         'type': 'Group',
    #         'data': {
    #             'name': 'temp_user_group'
    #         }
    #     }
    #
    #     # [Update Testing] update object properties
    #     workflow_event_data = {
    #         # 'assignee': assignee,
    #         'description': f'a description from {request.node.name}',
    #         'name': f'name-{request.node.name}',
    #     }
    #
    #     # workflow_event.model.assignee = assignee
    #     workflow_event.model.description = workflow_event_data.get('description')
    #     workflow_event.model.name = workflow_event_data.get('name')
    #
    #     # [Update Testing] submit the object to the TC API
    #     workflow_event.submit()
    #
    #     # [Retrieve Testing] get the object from the API
    #     workflow_event.get(all_available_fields=True)
    #
    #     # [Retrieve Testing] run assertions on returned data
    #     # assert workflow_event.model.assignee.type == assignee.get('type')
    #     # assert workflow_event.model.assignee.data.name == assignee.get('data').get('name')
    #     assert workflow_event.model.description == workflow_event_data.get('description')
    #     assert workflow_event.model.name == workflow_event_data.get('name')

