# -*- coding: utf-8 -*-
"""Test the TcEx Case Management Module."""
import os
from datetime import datetime, timedelta
from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


class TestWorkflowEvent:
    """Test TcEx CM Workflow Event Interface."""

    cm = None
    cm_helper = None
    test_obj = None
    test_obj_collection = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm
        self.test_obj = self.cm.workflow_event()
        self.test_obj_collection = self.cm.workflow_events()

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper(self.cm)

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_workflow_event_filter_keywords(self):
        """Test filter keywords."""
        # print(self.test_obj._doc_string)
        # print(self.test_obj_collection._filter_map_method)
        # print(self.test_obj_collection._filter_class)
        for keyword in self.test_obj_collection.filter.keywords:
            if keyword not in self.test_obj_collection.filter.implemented_keywords:
                assert False, f'Missing TQL keyword {keyword}.'

    def test_workflow_event_properties(self):
        """Test properties."""
        for prop_string, prop_data in self.test_obj.properties.items():
            prop_read_only = prop_data.get('read-only', False)
            prop_string = self.cm_helper.camel_to_snake(prop_string)

            # ensure class has property
            assert hasattr(
                self.test_obj, prop_string
            ), f'Missing {prop_string} property. read-only: {prop_read_only}'

    def test_workflow_event_create_by_case_id(self, request):
        """Test Workflow Event Creation"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # get workflow event from API to use in asserts
        workflow_event = self.cm.workflow_event(id=workflow_event.id)
        workflow_event.get()

        # run assertions on returned data
        assert workflow_event.summary == workflow_event_data.get('summary')

    # def test_workflow_event_delete_by_id(self, request):
    #     """Test Workflow Event Creation"""
    #     # create case
    #     case = self.cm_helper.create_case()

    #     # workflow event data
    #     workflow_event_data = {
    #         'case_id': case.id,
    #         'summary': request.node.name,
    #     }

    #     # create workflow_event
    #     workflow_event = self.cm.workflow_event(**workflow_event_data)
    #     workflow_event.submit()

    #     # get single workflow event
    #     workflow_event = self.cm.workflow_event(id=workflow_event.id)
    #     workflow_event.get()

    #     # delete the workflow event
    #     workflow_event.delete()

    #     # get single workflow event
    #     workflow_event = self.cm.workflow_event(id=workflow_event.id)
    #     workflow_event.get()

    #     # workflow action don't actually get deleted, the deleted flag gets set to True
    #     assert workflow_event.deleted is True

    def test_workflow_event_get_many(self, request):
        """Test Workflow Event Creation"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # iterate over all workflow events looking for needle
        for we in self.cm.workflow_events():
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False

    def test_workflow_event_get_single_by_id(self, request):
        """Test Workflow Event Creation"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # get workflow event from API to use in asserts
        workflow_event = self.cm.workflow_event(id=workflow_event.id)
        workflow_event.get(all_available_fields=True)

        # run assertions on returned data
        assert workflow_event.summary == workflow_event_data.get('summary')

    def test_workflow_event_get_by_tql_filter_case_id(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.case_id(TQL.Operator.EQ, case.id)

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    def test_workflow_event_get_by_tql_filter_date_added(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.date_added(
            TQL.Operator.GT, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    def test_workflow_event_get_by_tql_filter_deleted(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.deleted(TQL.Operator.EQ, False)

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    # def test_workflow_event_get_by_tql_filter_deleted_reason(self, request):
    #     """Test Workflow Event Get by TQL"""
    #     # create case
    #     case = self.cm_helper.create_case()

    #     # workflow event data
    #     workflow_event_data = {
    #         'case_id': case.id,
    #         'summary': request.node.name,
    #     }

    #     # create workflow_event
    #     workflow_event = self.cm.workflow_event(**workflow_event_data)
    #     workflow_event.submit()

    #     # delete event
    #     workflow_event.delete()

    #     # retrieve workflow event using TQL
    #     workflow_events = self.cm.workflow_events()
    #     workflow_events.filter.deleted(TQL.Operator.EQ, True)
    #     workflow_events.filter.deleted_reason(
    #         TQL.Operator.EQ, f"Deleted through API by User:{os.getenv('API_ACCESS_ID')}"
    #     )

    #     for we in workflow_events:
    #         # more than one workflow event will always be returned
    #         if we.summary == workflow_event_data.get('summary'):
    #             break
    #     else:
    #         assert False, 'No workflow event returned for TQL'

    def test_workflow_event_get_by_tql_filter_event_date(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'event_date': (datetime.now() + timedelta(days=1)).isoformat(),
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.case_id(TQL.Operator.EQ, case.id)
        workflow_events.filter.event_date(TQL.Operator.GT, datetime.now().strftime('%Y-%m-%d'))

        for we in workflow_events:  # pylint: disable=unused-variable
            # more than one workflow event will always be returned
            if workflow_event.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    def test_workflow_event_get_by_tql_filter_id(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.id(TQL.Operator.EQ, workflow_event.id)

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    # link is not added when the workflow event is created via the API
    # def test_workflow_event_get_by_tql_filter_link(self, request):
    #     """Test Workflow Event Get by TQL"""

    # link_text is not added when the workflow event is created via the API
    # def test_workflow_event_get_by_tql_filter_link_text(self, request):
    #     """Test Workflow Event Get by TQL"""

    def test_workflow_event_get_by_tql_filter_summary(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.summary(TQL.Operator.EQ, workflow_event_data.get('summary'))

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    def test_workflow_event_get_by_tql_filter_system_generated(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.case_id(TQL.Operator.EQ, case.id)
        workflow_events.filter.system_generated(TQL.Operator.EQ, False)

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    def test_workflow_event_get_by_tql_filter_tql(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.tql(f'caseid EQ {case.id}')

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'

    def test_workflow_event_get_by_tql_filter_username(self, request):
        """Test Workflow Event Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # workflow event data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # retrieve workflow event using TQL
        workflow_events = self.cm.workflow_events()
        workflow_events.filter.case_id(TQL.Operator.EQ, case.id)
        workflow_events.filter.username(TQL.Operator.EQ, os.getenv('API_ACCESS_ID'))

        for we in workflow_events:
            # more than one workflow event will always be returned
            if we.summary == workflow_event_data.get('summary'):
                break
        else:
            assert False, 'No workflow event returned for TQL'
