# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
import time
from tcex.case_management.tql import TQL

from ..tcex_init import tcex
from .cm_helpers import CMHelper


class TestTask:
    """Test TcEx CM Task Interface."""

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

    def test_task_create_by_case_id(self, request):
        """Test Task Creation"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            # 'is_workflow': False,
            'name': f'name-{request.node.name}',
            # 'source': f'source-{request.node.name}',
            # 'workflow_id': randint(100,999),
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # run assertions on returned data
        assert task.description == task_data.get('description')
        assert task.is_workflow == task_data.get('is_workflow')
        assert task.name == task_data.get('name')
        assert task.source == task_data.get('source')
        assert task.workflow_phase == task_data.get('workflow_phase')
        assert task.workflow_step == task_data.get('workflow_step')

    def test_task_create_by_case_xid(self, request):
        """Test Task Creation"""
        # create case
        case_xid = f'{request.node.name}-{time.time()}'
        self.cm_helper.create_case(xid=case_xid)

        # task data
        task_data = {
            'case_xid': case_xid,
            'description': f'a description from {request.node.name}',
            # 'is_workflow': False,
            'name': f'name-{request.node.name}',
            # 'source': f'source-{request.node.name}',
            # 'workflow_id': randint(100,999),
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # run assertions on returned data
        assert task.description == task_data.get('description')
        assert task.is_workflow == task_data.get('is_workflow')
        assert task.name == task_data.get('name')
        assert task.source == task_data.get('source')
        assert task.workflow_phase == task_data.get('workflow_phase')
        assert task.workflow_step == task_data.get('workflow_step')

    def test_task_delete_by_id(self, request):
        """Test Artifact Deletion"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # delete the artifact
        task.delete()

        # test artifact is deleted
        try:
            task.get()
            assert False
        except RuntimeError:
            pass

    def test_task_get_many(self, request):
        """Test Task Get Many"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # iterate over all tasks looking for needle
        for t in self.cm.tasks():
            if t.name == task_data.get('name'):
                assert task.description == task_data.get('description')
                break
        else:
            assert False

    def test_task_get_single_by_id(self, request):
        """Test Task Get Many"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            # 'is_workflow': False,
            'name': f'name-{request.node.name}',
            # 'source': f'source-{request.node.name}',
            # 'workflow_id': randint(100,999),
            'workflow_phase': 0,
            'workflow_step': 1,
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # get task from API to use in asserts
        task = self.cm.task(id=task.id)
        task.get()

        # run assertions on returned data
        assert task.description == task_data.get('description')
        # assert task.is_workflow == task_data.get('is_workflow')
        assert task.name == task_data.get('name')
        # assert task.source == task_data.get('source')
        assert task.workflow_phase == task_data.get('workflow_phase')
        assert task.workflow_step == task_data.get('workflow_step')

    def test_task_get_by_tql_filter_case(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_case_id(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve artifacts using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)

        assert len(tasks.as_dict) == 1
        for task in tasks:
            assert task.description == task_data.get('description')
            # assert task.is_workflow == task_data.get('is_workflow')
            assert task.name == task_data.get('name')
            # assert task.source == task_data.get('source')

    def test_task_get_by_tql_filter_completed_date(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_config_playbook(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_config_task(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_description(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve artifacts using TQL
        tasks = self.cm.tasks()
        tasks.filter.description(TQL.Operator.EQ, task_data.get('description'))

        assert len(tasks.as_dict) == 1
        for task in tasks:
            assert task.description == task_data.get('description')
            # assert task.is_workflow == task_data.get('is_workflow')
            assert task.name == task_data.get('name')
            # assert task.source == task_data.get('source')

    def test_task_get_by_tql_filter_due_date(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_duration(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_id(self, request):
        """Test Task Get by TQL"""

    # @bpurdy - is this a valid filter for task
    def test_task_get_by_tql_filter_intel_type(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_name(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_status(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_target_id(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_target_type(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_xid(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve artifacts using TQL
        tasks = self.cm.tasks()
        tasks.filter.xid(TQL.Operator.EQ, task_data.get('xid'))

        assert len(tasks.as_dict) == 1
        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
