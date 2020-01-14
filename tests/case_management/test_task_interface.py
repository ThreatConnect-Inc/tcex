# -*- coding: utf-8 -*-
"""Test the TcEx Threat Intel Module."""
import os
import time
from datetime import datetime, timedelta
from tcex.case_management.tql import TQL

from .cm_helpers import CMHelper, TestCaseManagement


class TestTask(TestCaseManagement):
    """Test TcEx CM Task Interface."""

    def setup_method(self):
        """Configure setup before all tests."""
        self.cm_helper = CMHelper('task')
        self.cm = self.cm_helper.cm
        self.tcex = self.cm_helper.tcex

    def teardown_method(self):
        """Configure teardown before all tests."""
        if os.getenv('TEARDOWN_METHOD') is None:
            self.cm_helper.cleanup()

    def test_task_api_options(self):
        """Test filter keywords."""
        super().obj_api_options()

    def test_task_code_gen(self):
        """Generate code and docstring from Options methods.

        This is not truly a test case, but best place to store it for now.
        """
        doc_string, filter_map, filter_class = super().obj_code_gen()
        assert doc_string
        assert filter_map
        assert filter_class
        print(filter_class)

    def test_task_filter_keywords(self):
        """Test filter keywords."""
        super().obj_filter_keywords()

    def test_task_object_properties(self):
        """Test properties."""
        super().obj_properties()

    def test_task_object_properties_extra(self):
        """Test properties."""
        super().obj_properties_extra()

    def test_task_create_by_case_id(self, request):
        """Test Task Creation"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
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
        assert task.name == task_data.get('name')
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
            'name': f'name-{request.node.name}',
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
        assert task.name == task_data.get('name')
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
            'name': f'name-{request.node.name}',
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
        assert task.name == task_data.get('name')
        assert task.workflow_phase == task_data.get('workflow_phase')
        assert task.workflow_step == task_data.get('workflow_step')

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

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_completed_date(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'completed_date': datetime.now().isoformat(),
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
        tasks.filter.completed_date(
            TQL.Operator.GT, (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

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
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.description(TQL.Operator.EQ, task_data.get('description'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_due_date(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'due_date': (datetime.now() + timedelta(days=1)).isoformat(),
            'name': f'name-{request.node.name}',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve artifacts using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.due_date(TQL.Operator.GT, datetime.now().strftime('%Y-%m-%d'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    # Per converstion with MJ this only works with templates
    # def test_task_get_by_tql_filter_duration(self, request):
    #     """Test Task Get by TQL"""

    # TODO: this needs some consideration
    def test_task_get_by_tql_filter_hascase(self, request):
        """Test Task Get by TQL"""

    def test_task_get_by_tql_filter_id(self, request):
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
        tasks.filter.id(TQL.Operator.EQ, task.id)
        tasks.filter.description(TQL.Operator.EQ, task_data.get('description'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_name(self, request):
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
        tasks.filter.name(TQL.Operator.EQ, task_data.get('name'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_status(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        task_data = {
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve artifacts using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.status(TQL.Operator.EQ, task_data.get('status'))

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_target_id(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        task_data = {
            'assignee': assignee,
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve artifacts using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.target_id(TQL.Operator.EQ, 5)

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

    def test_task_get_by_tql_filter_target_type(self, request):
        """Test Task Get by TQL"""
        # create case
        case = self.cm_helper.create_case()

        # task data
        assignee = self.cm.assignee(type='User', user_name=os.getenv('API_ACCESS_ID'))
        task_data = {
            'assignee': assignee,
            'case_id': case.id,
            'description': f'a description from {request.node.name}',
            'name': f'name-{request.node.name}',
            'status': 'Open',
            'xid': f'{request.node.name}-{time.time()}',
        }

        # create task
        task = self.cm.task(**task_data)
        task.submit()

        # retrieve artifacts using TQL
        tasks = self.cm.tasks()
        tasks.filter.case_id(TQL.Operator.EQ, case.id)
        tasks.filter.target_type(TQL.Operator.EQ, 'User')

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
            break
        else:
            assert False, 'No task returned for TQL'

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

        for task in tasks:
            assert task.description == task_data.get('description')
            assert task.name == task_data.get('name')
