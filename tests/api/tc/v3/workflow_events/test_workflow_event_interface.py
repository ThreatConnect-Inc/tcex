"""Test the TcEx API Module."""
# standard library
import os
import time
from datetime import datetime, timedelta

# third-party
import pytest
from pytest import FixtureRequest

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tests.api.tc.v3.v3_helpers import TestV3, V3Helper


class TestWorkflowEvents(TestV3):
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

        # [Create Testing] create the object object
        workflow_event = self.v3.workflow_event(**workflow_event_data)

        # [Create Testing] create the object to the TC API
        workflow_event.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        workflow_event = self.v3.workflow_event(id=workflow_event.model.id)

        # [Retrieve Testing] get the object from the API
        workflow_event.get()

    def test_workflow_event_all_filters(self, request: FixtureRequest):
        """Test TQL Filters for workflow_event on a Case"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create datetime in the past
        past = datetime.now() - timedelta(days=10)

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_id': case.model.id,
            'summary': request.node.name,
            'event_date': past,
        }

        # [Create Testing] create the object object
        workflow_event = self.v3.workflow_event(**workflow_event_data)

        # [Create Testing] create the object to the TC API
        workflow_event.create()

        # [Retrieving Testing] Retrieving the workflow event to ensure the user object is populated

        workflow_event.get(params={'fields': ['_all_']})

        # [Filter Testing] create the object collection
        workflow_events = self.v3.workflow_events()

        workflow_events.filter.case_id(TqlOperator.EQ, case.model.id)
        workflow_events.filter.date_added(TqlOperator.GT, past)
        workflow_events.filter.deleted(TqlOperator.EQ, False)
        # workflow_events.filter.event_date(TqlOperator.GT, past)
        workflow_events.filter.id(TqlOperator.EQ, workflow_event.model.id)
        # TODO: [PLAT-????] No link is generated/returned if workflow event is created via the api.
        # workflow_events.filter.link(TqlOperator.EQ, workflow_event.model.link)
        workflow_events.filter.summary(TqlOperator.EQ, workflow_event_data.get('summary'))
        workflow_events.filter.system_generated(TqlOperator.EQ, False)
        workflow_events.filter.user_name(TqlOperator.EQ, os.getenv('TC_API_ACCESS_ID'))
        # This filter does not work appropriately.
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
        case = self.v3_helper.create_case(xid=case_xid)

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_xid': case_xid,
            'summary': request.node.name,
        }

        # [Create Testing] create the object
        workflow_event = self.v3.workflow_event(**workflow_event_data)

        # [Create Testing] create the object to the TC API
        workflow_event.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        workflow_event = self.v3.workflow_event(id=workflow_event.model.id)

        # [Retrieve Testing] get the object from the API
        workflow_event.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        assert workflow_event.model.case_id == case.model.id

    # TODO: [PLAT-4118] this is waiting on a core fix
    # def test_workflow_event_delete_by_id(self, request: FixtureRequest):
    #     """Test WorkflowEvent Deletion"""
    #     # [Pre-Requisite] - create case and provide a unique xid
    #     case = self.v3_helper.create_case()

    #     # [Create Testing] define workflow_event data
    #     workflow_event_data = {
    #         'case_id': case.model.id,
    #         'summary': request.node.name,
    #     }

    #     # [Create Testing] create the object
    #     workflow_event = self.v3.workflow_event(**workflow_event_data)

    #     # [Create Testing] create the object to the TC API
    #     workflow_event.create()

    #     # [Retrieve Testing] create the object with id filter,
    #     # using object id from the object created above
    #     workflow_event = self.v3.workflow_event(id=workflow_event.model.id)

    #     workflow_event.model.deleted_reason = 'Pytesting'

    #     # [Delete Testing] remove the object
    #     workflow_event.delete()

    #     workflow_event.get()

    #     assert workflow_event.model.deleted
    #     assert workflow_event.model.deleted_reason == 'Pytesting'

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
                'summary': 'a description from pytest test',
            }

            # [Create Testing] create the object
            workflow_event = self.v3.workflow_event(**workflow_event_data)

            # [Create Testing] create the object to the TC API
            workflow_event.create()
            workflow_event_ids.append(workflow_event.model.id)

        # [Retrieve Testing] iterate over all object looking for needle
        workflow_events = self.v3.workflow_events(params={'resultLimit': 5})
        workflow_events.filter.case_id(TqlOperator.EQ, case.model.id)

        # [Retrieve Testing] One workflow event is auto created on creation of the case.
        assert len(workflow_events) == workflow_event_count + 1

        # [Retrieve Testing] Iterate over and verify each workflow_event + the one that was auto
        # created.
        for workflow_event in workflow_events:
            if workflow_event.model.id not in workflow_event_ids:
                workflow_event_ids.append(workflow_event.model.id)
            assert workflow_event.model.id in workflow_event_ids
            workflow_event_ids.remove(workflow_event.model.id)

        assert not workflow_event_ids, 'Not all workflow_events were returned.'

    def test_workflow_event_get_single_by_id_properties(self, request: FixtureRequest):
        """Test WorkflowEvent get single attached to workflow_event by id"""
        # [Pre-Requisite] - create case
        case_xid = f'{request.node.name}-{time.time()}'
        case = self.v3_helper.create_case(xid=case_xid)

        # [Pre-Requisite] - create datetime in the past
        past = datetime.now() - timedelta(days=10)

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_id': case.model.id,
            'case_xid': case_xid,
            'summary': request.node.name,
            'event_date': past,
        }

        # [Create Testing] init the workflow event object
        workflow_event = self.v3.workflow_event()

        # [Create Testing] testing setters on model
        workflow_event.model.case_id = workflow_event_data.get('case_id')
        workflow_event.model.case_xid = workflow_event_data.get('case_xid')
        workflow_event.model.summary = workflow_event_data.get('summary')
        workflow_event.model.event_date = workflow_event_data.get('event_date')

        # [Create Testing] create the object to the TC API
        workflow_event.create()

        # [Retrieve Testing] create the object with id filter,
        # using object id from the object created above
        workflow_event = self.v3.workflow_event(id=workflow_event.model.id)

        # [Retrieve Testing] get the object from the API
        workflow_event.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        assert workflow_event.model.case_id == workflow_event_data.get('case_id')
        assert workflow_event.model.summary == workflow_event_data.get('summary')
        assert workflow_event.model.event_date.strftime(
            '%Y-%m-%dT%H%M%S'
        ) == workflow_event_data.get('event_date').strftime('%Y-%m-%dT%H%M%S')

    def test_workflow_event_update_properties(self, request: FixtureRequest):
        """Test updating artifacts properties"""
        # [Pre-Requisite] - create case
        case = self.v3_helper.create_case()

        # [Pre-Requisite] - create datetime in the past
        past = datetime.now() - timedelta(days=10)

        # [Create Testing] define workflow_event data
        workflow_event_data = {
            'case_id': case.model.id,
            'summary': request.node.name,
            'event_date': past,
        }

        workflow_event = self.v3.workflow_event(**workflow_event_data)
        workflow_event.create()

        # [Pre-Requisite] - create datetime in the past
        past = datetime.now() - timedelta(days=8)

        # [Update Testing] update object properties
        workflow_event_data = {'event_date': past, 'summary': 'updated summary'}

        # workflow_event.model.assignee = assignee
        workflow_event.model.event_date = workflow_event_data.get('event_date')
        workflow_event.model.summary = workflow_event_data.get('summary')

        # [Update Testing] update the object to the TC API
        workflow_event.update()

        # [Retrieve Testing] get the object from the API
        workflow_event.get(params={'fields': ['_all_']})

        # [Retrieve Testing] run assertions on returned data
        assert workflow_event.model.event_date.strftime(
            '%Y-%m-%dT%H%M%S'
        ) == workflow_event_data.get('event_date').strftime('%Y-%m-%dT%H%M%S')
        assert workflow_event.model.summary == workflow_event_data.get('summary')
