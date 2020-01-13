# -*- coding: utf-8 -*-
"""Test the TcEx Case Management Module."""
import os

# import re
# import time
# from random import randint
# from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestWorkflowEvent(TestCaseManagement):
    """Test TcEx CM Workflow Event Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('workflow_template')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_workflow_template_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_workflow_template_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class

    def test_workflow_template_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_workflow_template_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_workflow_template_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    # def test_workflow_template_create_by_case_id(self, request):
    #     """Test Workflow Template Creation"""
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

    #     # get workflow event from API to use in asserts
    #     workflow_event = self.cm.workflow_event(id=workflow_event.id)
    #     workflow_event.get()

    #     # run assertions on returned data
    #     assert workflow_event.summary == workflow_event_data.get('summary')
