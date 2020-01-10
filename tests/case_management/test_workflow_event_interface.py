# -*- coding: utf-8 -*-
"""Test the TcEx Case Management Module."""
import os

# import re
# import time
# from random import randint
# from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


class TestWorkflowEvent:
    """Test TcEx CM Workflow Event Interface."""

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

    def test_workflow_event_properties(self):
        """Test WorkflowEvent properties."""
        r = tcex.session.options('/v3/workflowEvents', params={'show': 'readOnly'})
        for prop_string, prop_data in r.json().items():
            prop_read_only = prop_data.get('read-only', False)
            prop_string = self.cm_helper.camel_to_snake(prop_string)
            # prop_type = prop_data.get('type')

            # prop_required = False
            # if not prop_read_only:
            #     prop_required = prop_data.get('required')

            # ensure class has property
            assert hasattr(
                self.cm.workflow_event(), prop_string
            ), f'Workflow Event missing {prop_string} property. read-only: {prop_read_only}'

    def test_workflow_event_create_by_case_id(self, request):
        """Test Workflow Event Creation"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
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

    def test_workflow_event_delete_by_id(self, request):
        """Test Workflow Event Creation"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
        workflow_event_data = {
            'case_id': case.id,
            'summary': request.node.name,
        }

        # create workflow_event
        workflow_event = self.cm.workflow_event(**workflow_event_data)
        workflow_event.submit()

        # get single workflow event
        workflow_event = self.cm.workflow_event(id=workflow_event.id)
        workflow_event.get()

        # delete the workflow event
        workflow_event.delete()

        # get single workflow event
        workflow_event = self.cm.workflow_event(id=workflow_event.id)
        workflow_event.get()

        # workflow action don't actually get deleted, the deleted flag gets set to True
        assert workflow_event.deleted is True

    def test_workflow_event_get_many(self, request):
        """Test Workflow Event Creation"""
        # create case
        case = self.cm_helper.create_case()

        # artifact data
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

        # artifact data
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
