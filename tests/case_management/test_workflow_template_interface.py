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
    test_obj = None
    test_obj_collection = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.cm = tcex.cm
        self.test_obj = self.cm.workflow_template()
        self.test_obj_collection = self.cm.workflow_templates()

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper(self.cm)

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_workflow_template_filter_keywords(self):
        """Test filter keywords."""
        # print(self.test_obj._doc_string)
        # print(self.test_obj_collection._filter_map_method)
        # print(self.test_obj_collection._filter_class)
        for keyword in self.test_obj_collection.filter.keywords:
            if keyword not in self.test_obj_collection.filter.implemented_keywords:
                assert False, f'Missing TQL keyword {keyword}.'

    def test_workflow_template_properties(self):
        """Test properties."""
        for prop_string, prop_data in self.test_obj.properties.items():
            prop_read_only = prop_data.get('read-only', False)
            prop_string = self.cm_helper.camel_to_snake(prop_string)

            # ensure class has property
            assert hasattr(
                self.test_obj, prop_string
            ), f'Missing {prop_string} property. read-only: {prop_read_only}'

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
